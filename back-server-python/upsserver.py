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
world_seq_nums=[]
amazon_seq_nums=[]
def recv_msg(socket_) -> str:
    var_int_buff = []
    while True:
        print(socket_)
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
    whole_message = socket_.recv(msg_len)
    return whole_message, False

def send_message_to_world(socket,msg):
     string_msg = msg.SerializeToString()
     print(msg)
     world_socket_lock.acquire()
     _EncodeVarint(socket.send, len(string_msg), None)
     socket.send(string_msg)
     print("Please wait 2 seconds to send message to world")
     world_socket_lock.release()
     time.sleep(2)


def send_message_to_amazon(socket,msg):
    string_msg = msg.SerializeToString()
    amazon_socket_lock.acquire()
    _EncodeVarint(socket.send, len(string_msg), None)
    socket.send(string_msg)
    print("Please wait 2 seconds to send message to amazon")
    amazon_socket_lock.release()
    time.sleep(2)
def send_message_to_world_and_check_ack(socket,msg,seqnum,pure_ack):#same as method below
    global world_acked_num
    while True:
        all_acked = True
        if pure_ack == True:
            print("send world message is ")
            print(msg)
            print("send world  message that that")
            send_message_to_world(socket, msg)
            break
        for seqnums in seqnum:
            print("world acked num is:::::")
            print(world_acked_num)
            print("world acked num here::::::")
            if world_acked_num.count(seqnums)==0:
                all_acked = False
                break
        if len(world_acked_num)==0:
            all_acked=False
        if all_acked == True and pure_ack==False:
            break
        send_message_to_world(socket, msg)
def send_message_to_amazon_and_check_ack(socket,msg,seqnum,pure_ack):# method for continue send message until ack got, you can create a thread for the method
    global amazon_acked_num
    uacommands=amazon_ups_pb2.UACommands()
    if(type(msg)!=type(uacommands)):
        print("How come!!!!!!!!!!!")
        raise Exception()
    print(type(msg))
    print("msg is: "+str(msg))
    print("seqnum is:"+str(seqnum))
    while True:
        # print("send message!!!!")
        all_acked=True
        #print("alist is:"+str(amazon_acked_num))
        if pure_ack==True:
            print("message is send!!!!!!!!")
            print("socket is::::"+str(socket))
            print("amazon message is::"+str(msg))
            print(msg)
            print("message type::"+str(msg))
            send_message_to_amazon(socket,msg)
            print("send success!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            break
        for seqnums in seqnum:
             if amazon_acked_num.count(seqnums)==0:
                 all_acked=False
                 break
        if len(amazon_acked_num)==0:
            all_acked=False
        if all_acked==True and pure_ack==False:
              break
        send_message_to_amazon(socket, msg)
def handle_front_end(databaseconnection,socket_to_front,socket_to_world,socket_to_amazon):
     #update destination address, need modify
     global request_world_seqnum
     global request_amazon_seqnum
     while True:
         msg=socket_to_front.recv(1024)
         uacommand=amazon_ups_pb2.UACommands()
         uaseqnum=[]
         if len(msg)<0:
             print("connect error for frontend!!!!!")
             break
         else:
             print("front end"+str(msg))
             msg=msg.decode('utf-8')
             print("msg after decode::::"+str(msg))
             msg_arr=msg.split(",")
             oid=int(msg_arr[0])
             destx=int(msg_arr[1])
             desty=int(msg_arr[2])
             amazon_seq_lock.acquire()
             request_amazon_seqnum+=1
             uaseqnum.append(request_amazon_seqnum)
             amazon_seq_lock.release()
             destinationupdated1=protocol_buffer.to_UADestinationUpdated(oid,destx,desty,request_amazon_seqnum)
             print("Finished parsing!!!!!")
             uacommand.destinationupdated.append(destinationupdated1)
             amazonThread=Thread(target=send_message_to_amazon_and_check_ack,args=(socket_to_amazon,uacommand,uaseqnum,False))
             amazonThread.start()
             print("front end send success!!!!!!!!!")
def connect_frontend_socket(databaseconnection,socket_to_world,socket_to_amz, frontip,frontport):
    try:
        print("connect to frontend")
        ip_port_frontend = ('0.0.0.0', 8080)
        s_to_frontend = socket.socket()
        s_to_frontend.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s_to_frontend.bind(ip_port_frontend)
        s_to_frontend.listen(5)
        while True:
            frontend, _ = s_to_frontend.accept()
            frontthread=Thread(target=handle_front_end,args=(databaseconnection,frontend,socket_to_world,socket_to_amz))
            frontthread.start()
    except Exception as ex:
        print(ex)

def connect_world_socket():
    world_host = 'vcm-30499.vm.duke.edu'
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
        print(message)
        uconnected.ParseFromString(message)
        print("connect result is:::::: ")
        print(uconnected)
        print(uconnected.result)
        print(uconnected.worldid)
        print("connect result that!!!!!!")
        return uconnected
    except:
         print("Error: receiving UConnected error")
         sys.exit(1)

def connect_to_amazon(ip,port):
    print("ip:"+str(ip))
    print("port"+str(port))
    print(type(port))
    world_info = (ip, port)
    socket_to_amazon = socket.socket()
    try:
        socket_to_amazon.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        socket_to_amazon.connect(world_info)
        print("connect to amazon" + " ip is: "+str(ip)+"port is: "+str(port))
        return socket_to_amazon
    except:
        print("having problem in connectiong to amazon\n")
        socket_to_amazon.close()
        sys.exit(1)
def handle_world_ack(responses):
    global world_acked_num
    for ack1 in responses.acks:
        if world_acked_num.count(ack1)>0:
            continue
        else:
            world_ack_lock.acquire()
            world_acked_num.append(ack1)
            world_ack_lock.release()
def handle_amazon_ack(command):
    global amazon_acked_num
    for ack1 in command.acks:
        if len(amazon_acked_num)>0 and amazon_acked_num.count(ack1)>0:
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
   global world_seq_nums
   while amazon_connect_world is False:
         # print("Please wait amazon to connect world")
         i=1
   print("amazon connected!!!!!!!!")
   uconnectmessage=world_ups_pb2.UConnect()
   uconnectmessage.worldid=world_id
   uconnectmessage.isAmazon=False
   truckid=0
   for i in range(20):
        for j in range(20):
            uinittruck=protocol_buffer.to_UInitTruck(truckid,i,j)
            uconnectmessage.trucks.append(uinittruck)
            addTruck(database_connect,truckid,i,j,"idle")
            truckid=truckid+1
   ud=uconnect_world(uconnectmessage,world_socket)
   print("The ud is::::::;"+ud.result)
   if ud.result!="connected!":
       print("connect error!!!!!!!!!!")
   print("world connected!!!!!!!")
   global world_connected
   world_connected=True
   while True:
         message,noexception=recv_msg(world_socket)
         if noexception:
             #print("world connection error!!!!")
             break
         else:
            if 2==2:
                uResponseMessage = world_ups_pb2.UResponses()
                ucommand = world_ups_pb2.UCommands()
                uacommand = amazon_ups_pb2.UACommands()
                print("recieve from the world")
                print(uResponseMessage)
                print("receive from the world")
                wseqnum = []  # the seqnum that need check ack for world
                aseqnum = []  # the seqnum that need check ack for amazon
                if 1 == 1:
                    try:
                        uResponseMessage.ParseFromString(message)
                        print("message is:::::")
                        print(uResponseMessage)
                        print("message that::::::")
                        handle_world_ack(uResponseMessage)
                    except:
                        continue
                    count = 0
                    for ufinish in uResponseMessage.completions:
                        count += 1
                        ucommand.acks.append(ufinish.seqnum)
                        truckinfo = getTruckStatus(database_connect, ufinish.truckid)
                        print("truck info is:" + str(truckinfo))
                        if ufinish.status== "IDLE" or ufinish.status=="idle":
                            dinfo = getCurrDelivery(database_connect, ufinish.truckid)
                            for dinfos in dinfo:
                                print("dinfos"+str(dinfos))
                                updateDeliveryStatus(database_connect, dinfos[1], "delivered")
                                updateTruckStatus(database_connect, dinfos[3], "idle")
                                print("update truck status success!!!!!!")
                                pid=dinfos[1]
                                destx=dinfos[4]
                                desty=dinfos[5]
                                print("no syntax error")
                                print(pid)
                                print(destx)
                                print(desty)
                                amazon_seq_lock.acquire()
                                request_amazon_seqnum+=1
                                amazon_seq_lock.release()
                                print("lock correct")
                                aseqnum.append(request_amazon_seqnum)
                                print("append success!!!!!")
                                deliveredorder=protocol_buffer.to_UAOrderDelivered(pid, destx, desty,request_amazon_seqnum)
                                print("buffer start success!!!!!!!!")
                                uacommand.orderdelivered.append(deliveredorder)
                                print("ua delivered is:::"+str(uacommand))
                        else:
                            if truckinfo[0][0] == "gopickup":
                                wx = ufinish.x
                                wy = ufinish.y
                                winfo = get_warehouse_id(database_connect, wx, wy)
                                print(winfo)
                                wid = winfo[0][0]
                                print("wid" + str(wid))
                                truck_id = ufinish.truckid
                                amazon_seq_lock.acquire()
                                request_amazon_seqnum += 1
                                aseqnum.append(request_amazon_seqnum)
                                amazon_seq_lock.release()
                                uatruckarrive = amazon_ups_pb2.UATruckArrived()
                                uatruckarrive.whnum = wid
                                uatruckarrive.truckid = truck_id
                                uatruckarrive.seqnum = request_amazon_seqnum
                                uacommand.truckarrived.append(uatruckarrive)
                                updateTruckStatus(database_connect, truck_id, "arrive warehouse")
                    for delivermade in uResponseMessage.delivered:
                        count += 1
                        ucommand.acks.append(delivermade.seqnum)
                        pid = delivermade.packageid
                        updateDeliveryStatus(database_connect, pid, "delivered")
                        dinfo = get_delivery(database_connect, pid)
                        destx = dinfo[0][4]
                        desty = dinfo[0][5]
                        uaorderdelivered = amazon_ups_pb2.UAOrderDelivered()
                        uaorderdelivered.packageid = pid
                        uaorderdelivered.destinationx = destx
                        uaorderdelivered.destinationy = desty
                        amazon_seq_lock.acquire()
                        request_amazon_seqnum += 1
                        aseqnum.append(request_amazon_seqnum)
                        amazon_seq_lock.release()
                        uaorderdelivered.seqnum = request_amazon_seqnum
                        uacommand.orderdelivered.append(uaorderdelivered)
                        # updateTruckStatus(database_connect, truck_id, "delivered")
                        ids=get_delivery_orderid(database_connect,pid)
                        print("ids get correctly!!!!!!!!!!")
                        print("ids are"+str(ids))
                        for idorder in ids:
                            print("idorder 0 is::"+str(idorder[0]))
                            add_order_status(database_connect, idorder[0], "delivered")
                        print("add order status successfuly")
                    for err in uResponseMessage.error:
                        ucommand.acks.append(err.seqnum)
                    pureack = False
                    if len(wseqnum) == 0:
                        pureack = True
                    if count == 0:
                        continue
                    worldthread = Thread(target=send_message_to_world_and_check_ack,
                                         args=(world_socket, ucommand, wseqnum, pureack))
                    worldthread.start()
                    if len(aseqnum) == 0:
                        pureack = True
                    else:
                        pureack = False
                    if count > 0:
                        print("uuuuuuuuuuuuuuuuuuuuuuuuuuuuu")
                        print(uacommand)
                        amazonThread = Thread(target=send_message_to_amazon_and_check_ack,
                                              args=(amazon_socket, uacommand, aseqnum, pureack))
                        amazonThread.start()
                    # send ack number back to world
             #except:
             #    print("world error!!!!!!!")
def create_start_delivery(databaseconnect,order_id,truck_id,package_id,description):
    orderinfo=get_order(databaseconnect,order_id)
    global request_world_seqnum
    for order in orderinfo:
        orderid=order[0]
        destx=order[2]
        desty=order[3]
        addDelivery(databaseconnect,package_id,orderid,truck_id,destx,desty,description,"ready")
        udeliverlocation=protocol_buffer.to_UDeliverLOcation(package_id,destx,desty)
        world_seq_lock.acquire()
        request_world_seqnum+=1
        world_seq_lock.release()
        ugodeliver=protocol_buffer.to_UGoDeliver(truck_id,[udeliverlocation],request_world_seqnum)
        updateDeliveryStatus(databaseconnect,package_id,"delivering")
        updateTruckStatus(databaseconnect,truck_id,"delivering")
        return ugodeliver

def pickup(databaseconnect,aurequesttruck,world_socket):
    ugopickup=world_ups_pb2.UGoPickup()
    ugopickup.whid=aurequesttruck.whnum
    pickedtruckid=0
    idletruck=0
    global request_world_seqnum
    for i in range(225):
        statusinfo=getTruckStatus(databaseconnect,i)
        if statusinfo[0][0]=="idle":
            pickedtruckid=i
            idletruck+=1
            updateTruckStatus(databaseconnect,i,"gopickup")
            break
    if idletruck==0:
         for j in range(400):
             statusinfo=getTruckStatus(databaseconnect,j)
             if statusinfo[0][0]=="arrive warehouse" or statusinfo[0][0]=="delivering":
                 pickedtruckid=j
                 updateTruckStatus(databaseconnect,j,"gopickup")
                 if statusinfo[0][0]=="delivering":
                     dinfo = getCurrDelivery(databaseconnect, j)
                     did_pid = {}
                     for delivery in dinfo:
                         did_pid.update({delivery[0], delivery[1]})
                         updateDeliveryStatus(databaseconnect,delivery[1] , "ready")
                 break
    ugopickup.truckid=pickedtruckid
    world_seq_lock.acquire()
    request_world_seqnum+=1
    ugopickup.seqnum=request_world_seqnum
    world_seq_lock.release()
    ugopickup.whid=aurequesttruck.whnum
    return ugopickup

def handle_amazon_connections(database_connect,world_socket,amazon_socket):
    print("called amazon handler!!!!")
    while True:
        message, exception = recv_msg(amazon_socket)
        print("message recieved :::"+str(message))
        global request_amazon_seqnum
        global request_world_seqnum
        global world_id
        global world_connected
        global amazon_seq_nums
        if exception:
            print("world connection error1!!!!")
            break
        else:
            aucommand = amazon_ups_pb2.AUCommands()
            uacommand=amazon_ups_pb2.UACommands()
            ucommand=world_ups_pb2.UCommands()
            uaseqnum=[]
            wseqnum=[]
            just_order_created=False
            if 1==1:
                print("amazon msg: ", message)
                aucommand.ParseFromString(message)
                print("aucommand is received")
                print(type(aucommand))
                print(aucommand)
                print("received aucommand is")
                handle_amazon_ack(aucommand)
                other=0
                for thisorder in aucommand.ordercreated:
                       if amazon_seq_nums.count(thisorder.seqnum)>0:
                           uacommand.acks.append(thisorder.seqnum)
                           other+=1
                           continue
                       other+=1
                       just_order_created=True
                       upsaccount = ""
                       for upsaccount in thisorder.upsaccount:
                           upsaccount = thisorder.upsaccount
                       addOrder(database_connect, thisorder.orderid, thisorder.upsaccount,
                                thisorder.destinationx, thisorder.destinationy)
                       uacommand.acks.append(thisorder.seqnum)
                       print(uacommand.acks)
                       add_order_status(database_connect,thisorder.orderid,"ready")
                for requests in aucommand.requesttruck:
                         if amazon_seq_nums.count(requests.seqnum)>0:
                             uacommand.acks.append(requests.seqnum)
                             other+=1
                             continue
                         other+=1
                         just_order_created=False
                         ugopickup=pickup(database_connect, requests, world_socket)
                         ucommand.pickups.append(ugopickup)
                         wseqnum.append(ugopickup.seqnum)
                         uacommand.acks.append(requests.seqnum)
                         add_warehouse(database_connect,requests.x,requests.y,requests.whnum)
                for loadedorder in aucommand.orderloaded:
                        if amazon_seq_nums.count(loadedorder.seqnum)>0:
                            uacommand.acks.append(loadedorder.seqnum)
                            other+=1
                            continue
                        other+=1
                        just_order_created=False
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
                        add_order_status(database_connect, loadedorder.orderid, "delivering")
                for worldinfo in aucommand.connectedtoworld:
                         other+=1
                         just_order_created=False
                         global world_id
                         print("received amazon!!!!!!!!!!!!!!!!")
                         world_id = worldinfo.worldid
                         global amazon_connect_world
                         amazon_connect_world = True
                         print("connect to world is called!!!!!!!!!!!!")
                         while world_connected == False:
                             print("Please wait ups connect world!!!!!!")
                             i2=1
                         uaconnectedtoworld = amazon_ups_pb2.UAConnectedToWorld()
                         uaconnectedtoworld.worldid = world_id
                         amazon_seq_lock.acquire()
                         request_amazon_seqnum = request_amazon_seqnum + 1
                         uaseqnum.append(request_amazon_seqnum)
                         uaconnectedtoworld.seqnum = request_amazon_seqnum
                         amazon_seq_lock.release()
                         uacommand.connectedtoworld.append(uaconnectedtoworld)
                         uacommand.acks.append(worldinfo.seqnum)
                for err1 in aucommand.error:
                        other+=1
                        uacommand.acks.append(err1.seqnum)
                for acked_number in uacommand.acks:
                    amazon_seq_nums.append(acked_number)
                #send command to amazon
                if other==0:
                    print("other!!!!!!!!!")
                    continue
                pureack=False
                if len(uaseqnum)==0:
                    print("true!!!!!!!!!")
                    pureack=True
                print("uaseqnumn:"+str(uaseqnum))
                print("here come!!!!!!!")
                print(uacommand)
                print("send command is: "+str(uacommand))
                print("is pureack?"+str(pureack))
                amazon_thread=Thread(target=send_message_to_amazon_and_check_ack,args=(amazon_socket,uacommand,uaseqnum,pureack))
                amazon_thread.start()
                print("amazon start successs!!!!")
                if len(wseqnum)==0:
                     pureack=True
                else:
                    pureack=False
                print("wseqnumn:" + str(wseqnum))
                if not just_order_created:
                    worldThread = Thread(target=send_message_to_world_and_check_ack,
                                         args=(world_socket, ucommand, wseqnum, pureack))
                    worldThread.start()
def connect_to_database():
    connect=psycopg2.connect(host="127.0.0.1",database="mini_ups",user="postgres",password="20230101")
    # connect.close()
    return connect
def create_database(connect):
    cur = connect.cursor()
    cur.execute("DROP TABLE IF EXISTS TRUCK CASCADE;")
    cur.execute("DROP TABLE IF EXISTS ORDERS CASCADE;")
    cur.execute("DROP TABLE IF EXISTS DELIVERY CASCADE;")
    cur.execute("DROP TABLE IF EXISTS ORDER_STATUS;")
    cur.execute("DROP TABLE IF EXISTS WAREHOUSE;")
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
                   PACKAGE_ID INT PRIMARY KEY,
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
    cur.execute('''CREATE TABLE IF NOT EXISTS ORDER_STATUS(
                         STATUS_ID SERIAL PRIMARY KEY,
                         OD_STATUS VARCHAR(256),
                         M_TIME TIMESTAMP,
                         ORDER_ID INT,
                         FOREIGN KEY (ORDER_ID) REFERENCES ORDERS(ORDER_ID) ON DELETE CASCADE ON UPDATE CASCADE
                         );''')
    print("Creating DELIVERY table")
    connect.commit()
amazon_ip="vcm-30499.vm.duke.edu" #可以随时更改
amazon_port=9090 #可以随时更改
database_connection1=connect_to_database()
create_database(database_connection1)
database_connection2=connect_to_database()
print("connect success!!!!!!")
world_socket=connect_world_socket()
amazon_socket=connect_to_amazon(amazon_ip,amazon_port)
print("connect success!!!!!!")
worldThread=Thread(target=handle_world_connections,args=(database_connection1,world_socket,amazon_socket))
amazonThread=Thread(target=handle_amazon_connections,args=(database_connection2,world_socket,amazon_socket))
front_ip="127.0.0.1"
front_port=8080
frontThread=Thread(target=connect_frontend_socket,args=(database_connection1,world_socket,amazon_socket,front_ip,front_port))
worldThread.start()
amazonThread.start()
frontThread.start()
worldThread.join()
amazonThread.join()
frontThread.join()
database_connection1.close()
database_connection2.close()