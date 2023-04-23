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

total_lock=threading.Lock()
world_socket_lock=threading.Lock()
amazon_socket_lock=threading.Lock()

world_connected=False
request_amazon_seqnum=0
request_world_seqnum=0
world_id=1
world_acked_num=[]
amazon_acked_num=[]

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
    while world_acked_num.count(seqnum)==0:
        send_message_to_world(socket,msg)

def send_message_to_amazon_and_check_ack(socket,msg,seqnum):# method for continue send message until ack got, you can create a thread for the method
    while amazon_acked_num.count(seqnum)==0:
        send_message_to_amazon(socket,msg)

def connect_world_socket():
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
    message, noexception = recv_msg(world_socket)
    uconnected=world_ups_pb2.UConnected()
    try:
        uconnected.ParseFromString(message)
        return uconnected
    except:
         print("connect world error!!!!")
         sys.exit(1)

def connect_to_amazon(ip,port):
    world_info = (ip, port)
    socket_to_amazon = socket.socket()
    try:
        socket_to_amazon.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        socket_to_amazon.connect(world_info)
        print("connect to world" + "\n")
        return socket_to_amazon
    except:
        print("having problem in connectiong to world\n")
        socket_to_amazon.close()
        sys.exit(1)

def handle_world_ack(responses):
    for ack1 in responses.acks():
        if world_acked_num.contains(ack1):
            continue
        else:
            total_lock.acquire()
            world_acked_num.append(ack1)
            total_lock.release()

def handle_amazon_ack(command):
    for ack1 in command.acks():
        if amazon_acked_num.count(ack1)>0:
            continue
        else:
            total_lock.acquire()
            amazon_acked_num.append(ack1)
            total_lock.release()

def handle_world_connections(database_connect,world_socket,amazon_socket):
    global world_connected
    UconnectMsg=world_ups_pb2.UConnect()
    #generate trucks
    trucks=[]
    truckid=0
    for i in range(10):
        for j in range(10):
           truck= protocol_buffer.to_UInitTruck(truckid,i,j)
           UconnectMsg.trucks.append(truck)
           truckid+=1
    UconnectMsg.isAmazon=False
    ud=uconnect_world(UconnectMsg,world_socket)
    global world_id
    world_id=ud.worldid()
    world_connected = True
    while True:
         message,noexception=recv_msg(world_socket)
         if not noexception:
             print("world connection error!!!!")
             break
         else:
             uResponseMessage=world_ups_pb2.UResponses()
             try:
                 uResponseMessage.ParseFromString(message)
                 if uResponseMessage.HasField("completions"):
                     #check truck status, whether it is pick up or finished all delivery
                     #if pick up finished, send UATruckArrived,else, update truck status to idle.
                     pass
                 elif uResponseMessage.HasField("delivered"):
                     #update delivery status, send UAOrderDelivered to amazon
                     pass
                 #send ack number back to world
             except:
                  print("response error")

def handle_amazon_connections(database_connect,world_socket,amazon_socket):
    while True :
        if world_connected:
            global request_amazon_seqnum
            total_lock.acquire()
            request_amazon_seqnum += 1
            total_lock.release()
            ua = protocol_buffer.to_UAConnectedToWorld(worldid=world_id,seqnum=request_amazon_seqnum)
            firstThread=Thread(target=send_message_to_amazon_and_check_ack(amazon_socket,ua,request_amazon_seqnum))
            firstThread.start()
            break
    while True:
        message, noexception = recv_msg(amazon_socket)
        if not noexception:
            print("world connection error!!!!")
            break
        else:
            aucommand = amazon_ups_pb2.AUCommands()
            try:
                aucommand.ParseFromString(message)
                for ack in aucommand.acks():
                    total_lock.acquire()
                    amazon_acked_num.append(ack)
                    total_lock.release()
                if aucommand.HasField("ordercreated"):
                    #create order
                    pass
                if aucommand.HasField("requesttruck"):
                    #call pick up
                    pass
                if aucommand.HasField("orderloaded"):
                    #call create Delivery and start Delivery, send order departure
                    pass
                #send ack back to amazon
            except:
                print("response error")

def connect_to_database():
    connect=psycopg2.connect(host="127.0.0.1",database="mini_ups",user="postgres",password="20230101")
    cur = connect.cursor()

    cur.execute("DROP TABLE IF EXISTS TRUCK CASCADE;")
    cur.execute("DROP TABLE IF EXISTS ORDER CASCADE;")
    cur.execute("DROP TABLE IF EXISTS DELIVERY CASCADE;")

    cur.execute("CREATE TABLE IF NOT EXISTS TRUCK(TRUCK_ID INT PRIMARY KEY, X INT, Y INT, T_STATUS VARCHAR(256));")
    print("Creating TRUCK table")

    cur.execute('''CREATE TABLE IF NOT EXISTS ORDER(
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
                FOREIGN KEY (ORDER_ID) REFERENCES ORDER(ORDER_ID) ON DELETE CASCADE ON UPDATE CASCADE
                );''')
    print("Creating DELIVERY table")
    connect.commit()
    connect.close()
    return connect

amazon_ip="" #可以随时更改
amazon_port=5555  #可以随时更改
world_socket=connect_world_socket()
amazon_socket=connect_to_amazon(amazon_ip,amazon_port)
database_connection=connect_to_database()
worldThread=Thread(target=handle_world_connections,args=(database_connection,world_socket,amazon_socket))
amazonThread=Thread(target=handle_amazon_connections,args=(database_connection,world_socket,amazon_socket))
worldThread.start()
amazonThread.start()



