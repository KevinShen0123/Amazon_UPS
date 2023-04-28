import django
import os
import sys
from concurrent.futures import ThreadPoolExecutor
import socket
from threading import Thread
import threading
import time
from google.protobuf.internal.decoder import _DecodeVarint32
import world_ups_pb2
from google.protobuf.internal.encoder import _EncodeVarint
import amazon_ups_pb2
import psycopg2
import protocol_buffer
from database_query import *
world_ack_lock=threading.Lock()
amazon_ack_lock=threading.Lock()
world_socket_lock=threading.Lock()
amazon_socket_lock=threading.Lock()
world_seq_lock=threading.Lock()
amazon_seq_lock=threading.Lock()
world_connected=False
request_amazon_seqnum=0
request_world_seqnum=0
world_id=1
world_acked_num=[]
amazon_acked_num=[]
amazon_connect_world=False

def recv_msg(socket_) -> str:
    var_int_buff = []
    while True:
        buf = socket_.recv(1)
        if len(buf) <= 0:  # socket closes
            return None, True
        var_int_buff += buf
        print(str(var_int_buff))
        try:
            msg_len, new_pos = _DecodeVarint32(var_int_buff, 0)
            if new_pos != 0:
                break
        except IndexError:
            print("Error in decoding msg\n")
            return None, False
    print("msg_len: " + str(msg_len) + "\n")
    whole_message = socket_.recv(msg_len)
    return whole_message, False

def send_message_to_world(socket,msg):
    string_msg = msg.SerializeToString()
    print(string_msg) 

    world_socket_lock.acquire()
    _EncodeVarint(socket.send, len(string_msg), None)
    socket.send(string_msg)
    world_socket_lock.release()

def send_message_to_amazon(socket,msg):
    string_msg = msg.SerializeToString()

    amazon_socket_lock.acquire()
    _EncodeVarint(socket.send, len(string_msg), None)
    socket.send(string_msg)
    amazon_socket_lock.release()

def send_message_to_world_and_check_ack(socket,msg,seqnum):#same as method below
    while True:
        all_acked = True
        for seqnums in seqnum:
            if amazon_acked_num.count(seqnums) == 0:
                all_acked = False
                break
        if all_acked == True:
            break
        send_message_to_world(socket, msg)

def send_message_to_amazon_and_check_ack(socket,msg,seqnum):# method for continue send message until ack got, you can create a thread for the method
    # while amazon_acked_num.count(seqnum)==0:
    #     send_message_to_amazon(socket,msg)
    while True:
        all_acked=True
        for seqnums in seqnum:
             if amazon_acked_num.count(seqnums)==0:
                 all_acked=False
                 break
        if all_acked==True:
              break
        send_message_to_amazon(socket,msg)

def handle_front_end(databaseconnection,socket_to_front,socket_to_world,socket_to_amazon):
     #update destination address
     while True:
         msg,noexception=recv_msg(socket_to_front)
         uacommand=amazon_ups_pb2.UACommands()
         uaseqnum=[]
         if not noexception:
             print("connect error for frontend!!!!!")
             break
         else:
             msg_arr=msg.split(",")
             pid=int(msg_arr[0])
             destx=int(msg_arr[1])
             desty=int(msg_arr[2])
             updateDeliveryStatus(databaseconnection,destx,desty)
             dinfo = get_delivery(databaseconnection, pid)
             oid = dinfo[0][2]
             amazon_seq_lock.acquire()
             request_amazon_seqnum+=1
             uaseqnum.append(request_amazon_seqnum)
             amazon_seq_lock.release()
             destinationupdated=protocol_buffer.to_UADestinationUpdated(oid,destx,desty,request_amazon_seqnum)
             uacommand.destinationupdated.append(destinationupdated)
             amazonThread=Thread(target=send_message_to_amazon_and_check_ack,args=(amazon_socket,uacommand,uaseqnum))
             amazonThread.start()

def connect_frontend_test(databaseconnection):
    try:
        print("dock to frontend")
        ip_port_frontend = ('127.0.0.1', 8080)
        s_to_frontend = socket.socket()
        s_to_frontend.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s_to_frontend.bind(ip_port_frontend)
        s_to_frontend.listen(5)
        while True:
            print("entering while")
            frontend, _ = s_to_frontend.accept()
            #t=Thread(target=handle_front_end,args=(databaseconnection,s_to_frontend,socket_to_world,socket_to_amz))
            #t.start()
            print("accepting")
            f_msg, ex = recv_msg(frontend)
            print("received")
            print(f_msg)
    except Exception as ex:
        print(ex)          
  
def connect_frontend_socket(databaseconnection,socket_to_world,socket_to_amz, frontip,frontport):
    try:
        print("dock to frontend")
        ip_port_frontend = ('0.0.0.0', 8888)
        s_to_frontend = socket.socket()
        s_to_frontend.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s_to_frontend.bind(ip_port_frontend)
        s_to_frontend.listen(5)
        while True:
            frontend, _ = s_to_frontend.accept()
            t=Thread(target=handle_front_end,args=(databaseconnection,s_to_frontend,socket_to_world,socket_to_amz))
            t.start()
    except Exception as ex:
        print(ex)

def connect_world_socket():
    #world_host = 'vcm-30760.vm.duke.edu'
    world_host = '127.0.0.1'
    world_info = (world_host, 12345)
    socket_to_world = socket.socket()
    try:
        socket_to_world.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        socket_to_world.connect(world_info)
        print("connect to world socket" + "\n")
        return socket_to_world
    except:
        print("having problem in connectiong to world\n")
        socket_to_world.close()
        sys.exit(1)

def uconnect_world(uconnectmessage,world_socket):
    send_message_to_world(world_socket, uconnectmessage)
    # receive uconnected from world
    message, noexception = recv_msg(world_socket)
    uconnected=world_ups_pb2.UConnected()
    print(message)
    try:
        uconnected.ParseFromString(message)
        return uconnected
    except:
         print("Error: receiving UConnected error")
         sys.exit(1)

def connect_to_amazon(ip,port):
    world_info = (ip, port)
    socket_to_amazon = socket.socket()
    try:
        socket_to_amazon.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        socket_to_amazon.connect(world_info)
        print("connect to amazon" + "\n")
        return socket_to_amazon
    except:
        print("having problem in connectiong to amazon\n")
        socket_to_amazon.close()
        sys.exit(1)

def handle_world_ack(responses):
    for ack1 in responses.acks():
        if world_acked_num.contains(ack1):
            continue
        else:
            world_ack_lock.acquire()
            world_acked_num.append(ack1)
            world_ack_lock.release()

def handle_amazon_ack(command):
    for ack1 in command.acks():
        if amazon_acked_num.count(ack1)>0:
            continue
        else:
            amazon_ack_lock.acquire()
            amazon_acked_num.append(ack1)
            amazon_ack_lock.release()

def handle_world_connections(database_connect,world_socket,amazon_socket):
   global request_world_seqnum
   global request_amazon_seqnum
   global amazon_connect_world
   global world_id
   while amazon_connect_world is False:
         #print("Please wait amazon to connect world")
         pass
   uconnectmessage=world_ups_pb2.UConnect()
   uconnectmessage.worldid=world_id
   uconnectmessage.isAmazon=False
   truckid=0
   for i in range(10):
        for j in range(10):
            uinittruck=protocol_buffer.to_UInitTruck(truckid,i,j)
            uconnectmessage.trucks.append(uinittruck)
            addTruck(database_connect,truckid,i,j,"idle")
            truckid=truckid+1
   ud=uconnect_world(uconnectmessage,world_socket)
   if ud.result!="connected":
       print("connect error!!!!!!!!!!")
   global world_connected
   world_connected=True
   while True:
         message,noexception=recv_msg(world_socket)
         print(message)
         if not noexception:
             print("world connection error!!!!")
             break
         else:
             uResponseMessage=world_ups_pb2.UResponses()
             ucommand=world_ups_pb2.UCommands()
             uacommand=amazon_ups_pb2.UACommands()
             wseqnum=[]
             aseqnum=[]
             try:
                 uResponseMessage.ParseFromString(message)
                 print("===="+uResponseMessage)
                 handle_world_ack(uResponseMessage)
                 if uResponseMessage.HasField("completions"):
                    for ufinish in uResponseMessage.completions:
                          ucommand.acks.append(ufinish.seqnum)
                          if ufinish.status=="idle":
                               dinfo=getCurrDelivery(database_connect,ufinish.truckid)
                               updateDeliveryStatus(database_connect,dinfo[1],"delivered")
                               updateTruckStatus(database_connect,dinfo[3],"idle")
                          else:
                            print(ufinish.status)
                            if ufinish.status=="arrive warehouse":
                                 wx=ufinish.x
                                 wy=ufinish.y
                                 winfo=get_warehouse_id(database_connect,wx,wy)
                                 wid=winfo[0][0]
                                 print("wid", wid)
                                 truck_id=ufinish.truckid
                                 amazon_seq_lock.acquire()
                                 request_amazon_seqnum+=1
                                 aseqnum.append(request_amazon_seqnum)
                                 amazon_seq_lock.release()
                                 uatruckarrive=amazon_ups_pb2.UATruckArrived()
                                 uatruckarrive.whnum=wid
                                 uatruckarrive.truckid=truck_id
                                 uatruckarrive.seqnum=request_amazon_seqnum
                                 uacommand.truckarrived.append(uatruckarrive)
                 if uResponseMessage.HasField("delivered"):
                     #update delivery status, send UAOrderDelivered to amazon
                        for delivermade in uResponseMessage.delivered:
                              ucommand.acks.append(delivermade.seqnum)
                              pid=delivermade.packageid
                              updateDeliveryStatus(database_connect,pid,"delivered")
                              dinfo=get_delivery(database_connect,pid)
                              destx=dinfo[0][4]
                              desty=dinfo[0][5]
                              uaorderdelivered=amazon_ups_pb2.UAOrderDelivered()
                              uaorderdelivered.packageid=pid
                              uaorderdelivered.destinationx=destx
                              uaorderdelivered.destinationy=desty
                              amazon_seq_lock.acquire()
                              request_amazon_seqnum+=1
                              aseqnum.append(request_amazon_seqnum)
                              amazon_seq_lock.release()
                              uaorderdelivered.seqnum=request_amazon_seqnum
                              uacommand.orderdelivered.append(uaorderdelivered)
                 if uResponseMessage.HasField("error"):
                     for err in uResponseMessage.error:
                          ucommand.acks.append(err.seqnum)
                 worldthread=Thread(target=send_message_to_world_and_check_ack,args=(world_socket,ucommand,wseqnum))
                 worldthread.start()
                 amazonThread=Thread(target=send_message_to_amazon_and_check_ack,args=(amazon_socket,uacommand,aseqnum))
                 amazonThread.start()
                 #send ack number back to world
                 print("receiving from world ....")
             except:
                  print("response error")
    
def create_start_delivery(databaseconnect,order_id,truck_id,package_id,description):
    orderinfo=get_order(databaseconnect,order_id)
    for order in orderinfo:
        orderid=order[0]
        destx=order[2]
        desty=order[3]
        addDelivery(databaseconnect,package_id,orderid,truck_id,destx,desty,description,"ready")
        udeliverlocation=protocol_buffer.to_UDeliverLOcation(package_id,destx,desty)
        world_seq_lock.acquire()
        request_world_seqnum+=1
        world_seq_lock.release()
        ugodeliver=protocol_buffer.to_UGoDeliver(truck_id,udeliverlocation,request_world_seqnum)
        updateDeliveryStatus(databaseconnect,package_id,"delivering")
        return ugodeliver

def pickup(databaseconnect,aurequesttruck,world_socket):
    ugopickup=world_ups_pb2.UGoPickup()
    ugopickup.whnum=aurequesttruck.whnum
    pickedtruckid=0
    idletruck=0
    for i in range(100):
        statusinfo=getTruckStatus(databaseconnect,i)
        if statusinfo[0][0]=="idle":
            pickedtruckid=i
            idletruck+=1
            updateTruckStatus(databaseconnect,i,"gopickup")
            break
    if idletruck==0:
         for j in range(100):
             statusinfo=getTruckStatus(databaseconnect,j)
             if statusinfo[0][0]=="arrive warehouse" or statusinfo[0][0]=="delivering":
                 pickedtruckid=j
                 updateTruckStatus(databaseconnect,j,"gopickup")
                 if statusinfo[0][0]=="delivering":
                     dinfo = getCurrDelivery(databaseconnect, j)
                     did_pid = {}
                     for delivery in dinfo:
                         did_pid.update({delivery[0], delivery[1]})
                     updateDeliveryStatus(databaseconnect, j, "ready")
                 break
    ugopickup.truckid=pickedtruckid
    world_seq_lock.acquire()
    request_world_seqnum+=1
    ugopickup.seqnum=request_world_seqnum
    world_seq_lock.release()
    ugopickup.whid=aurequesttruck.whnum
    return ugopickup

def handle_amazon_connections(database_connect,world_socket,amazon_socket):
    while True:
        message, noexception = recv_msg(amazon_socket)
        if not noexception:
            print("world connection error!!!!")
            break
        else:
            aucommand = amazon_ups_pb2.AUCommands()
            uacommand=amazon_ups_pb2.UACommands()
            ucommand=world_ups_pb2.UCommands()
            uaseqnum=[]
            wseqnum=[]
            try:
                print("amazon msg: ", message)
                aucommand.ParseFromString(message)
                handle_amazon_ack(aucommand)
                if aucommand.HasField("ordercreated"):
                    print("ordercre")
                    for thisorder in aucommand.ordercreated:
                       upsaccount = ""
                       if thisorder.HasField("upsaccount"):
                           upsaccount = thisorder.upsaccount
                       addOrder(database_connect, thisorder.orderid, thisorder.upsaccount,
                                thisorder.destinationx, thisorder.destinationy)
                       uacommand.acks.append(thisorder.seqnum)
                    
                if aucommand.HasField("requesttruck"):
                     print("reqquest")
                     for requests in aucommand.requesttruck:
                         ugopickup=pickup(database_connect, requests, world_socket)
                         ucommand.pickups.append(ugopickup)
                         wseqnum.append(ugopickup.seqnum)
                         uacommand.acks.append(requests.seqnum)
                         add_warehouse(database_connect,requests.x,requests.y,requests.whnum)
                if aucommand.HasField("orderloaded"):
                    print("order loaded")
                    #call create Delivery and start Delivery, send order departure
                    for loadedorder in aucommand.orderloaded:
                        uacommand.acks.append(loadedorder.seqnum)
                        ugodeliver=create_start_delivery(database_connect,loadedorder.orderid,loadedorder.truckid,loadedorder.packageid,loadedorder.description)
                        amazon_seq_lock.acquire()
                        request_amazon_seqnum+=1
                        uaseqnum.append(request_amazon_seqnum)
                        amazon_seq_lock.release()
                        uaorderdeparture=protocol_buffer.to_UAOrderDeparture(loadedorder.orderid,loadedorder.packageid,loadedorder.packageid,request_amazon_seqnum)
                        ucommand.deliveries.append(ugodeliver)
                        wseqnum.append(ugodeliver.seqnum)
                        uacommand.orderdeparture.append(uaorderdeparture)
                if aucommand.HasField("connectedtoworld"):
                     print("connect to world")
                     for worldinfo in aucommand.connectedtoworld:
                         world_id = worldinfo.worldid
                         amazon_connect_world = True
                         while world_connected == False:
                             print("Please wait ups connect world!!!!!!")
                         uaconnectedtoworld = amazon_ups_pb2.UAConnectedToWorld()
                         uaconnectedtoworld.worldid = world_id
                         amazon_seq_lock.acquire()
                         request_amazon_seqnum = request_amazon_seqnum + 1
                         uaseqnum.append(request_amazon_seqnum)
                         uaconnectedtoworld.seqnum = request_amazon_seqnum
                         amazon_seq_lock.release()
                         uacommand.connectedtoworld.append(uaconnectedtoworld)
                         uacommand.acks.append(world_id.seqnum)
                if aucommand.HasField("error"):
                    print("error")
                    for err1 in aucommand.error:
                        uacommand.acks.append(err1.seqnum)
                #send command to amazon
                amazon_thread=Thread(target=send_message_to_amazon_and_check_ack,args=(amazon_socket,uacommand,uaseqnum))
                amazon_thread.start()
                worldThread=Thread(target=send_message_to_world_and_check_ack,args=(world_socket,ucommand,wseqnum))
                worldThread.start()
            except:
              print("response error")

def connect_to_database():
    connect=psycopg2.connect(host="127.0.0.1",database="mini_ups",user="postgres",password="passw0rd")
    cur = connect.cursor()

    cur.execute("DROP TABLE IF EXISTS TRUCK CASCADE;")
    cur.execute("DROP TABLE IF EXISTS ORDERS CASCADE;")
    cur.execute("DROP TABLE IF EXISTS DELIVERY CASCADE;")

    cur.execute("CREATE TABLE IF NOT EXISTS TRUCK(TRUCK_ID INT PRIMARY KEY, X INT, Y INT, T_STATUS VARCHAR(256));")
    print("Creating TRUCK table")

    cur.execute('''CREATE TABLE IF NOT EXISTS ORDERS(
                ORDER_ID INT PRIMARY KEY,
                UPSACCOUNT VARCHAR(256),
                DEST_X INT,
                DEST_Y INT
                );''')
    print("Creating ORDER table")

    cur.execute('''CREATE TABLE IF NOT EXISTS DELIVERY(
                DELIVERY_ID SERIAL,
                PAKCAGE_ID INT PRIMARY KEY,
                ORDER_ID INT, 
                TRUCK_ID INT,
                DEST_X INT,
                DEST_Y INT,
                DESCR VARCHAR(256),
                D_STATUS VARCHAR(256),
                FOREIGN KEY (ORDER_ID) REFERENCES ORDERS(ORDER_ID) ON DELETE CASCADE ON UPDATE CASCADE
                );''')
    cur.execute('''CREATE TABLE IF NOT EXISTS WAREHOUSE(
                   X INT,
                   Y INT,
                   WHID INT PRIMARY KEY
                   );''')
    print("Creating DELIVERY table")
    connect.commit()
    # connect.close()
    return connect

amazon_ip="127.0.0.1" #可以随时更改
amazon_port=5432  #可以随时更改

amazon_socket=connect_to_amazon(amazon_ip,amazon_port)
world_socket=connect_world_socket()

database_connection1=connect_to_database()
handle_world_connections(database_connection1, world_socket, amazon_socket)
worldThread=Thread(target=handle_world_connections,args=(database_connection1,world_socket,amazon_socket))

database_connection2=connect_to_database()
amazonThread=Thread(target=handle_amazon_connections,args=(database_connection2,world_socket,amazon_socket))

#front_socket=connect_frontend_socket(front_ip,front_port)
#amazon_socket=connect_to_amazon(amazon_ip,amazon_port)

# connect_frontend_test(database_connection1)
#database_connection1=connect_to_database()
#handle_world_connections(database_connection1, world_socket, amazon_socket)
# worldThread=Thread(target=handle_world_connections,args=(database_connection1,world_socket,amazon_socket))

#
# #frontThread=Thread(target=connect_frontend_test,args=(database_connection1))
# amazonThread=Thread(target=handle_amazon_connections,args=(database_connection2,world_socket,amazon_socket))
# database_connection3=connect_to_database()
# #frontThread=Thread(target=connect_frontend_socket,args=(database_connection3,world_socket,amazon_socket,front_ip,front_port))
# worldThread.start()
# amazonThread.start()
# #frontThread.start()
# worldThread.join()
# amazonThread.join()
# #frontThread.join()
# database_connection1.close()
# database_connection2.close()
# database_connection3.close()
