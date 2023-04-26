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
world_connected=Fals
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

def send_message_to_ups(socket,msg):
    string_msg = msg.SerializeToString()

    amazon_socket_lock.acquire()
    _EncodeVarint(socket.send, len(string_msg), None)
    socket.send(string_msg)
    amazon_socket_lock.release()


test_server = ('127.0.0.1', 5432)
test_socket = socket.socket()
test_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# bind the listen port
test_socket.bind(test_server)
test_socket.listen(5)
print("socket bind to listen")

# accept from ups
accept_socket, _ = test_socket.accept()
print("connection accepted")

# generate AUCommands
auc  = amazon_ups_pb2.AUCommands()

# generate AUOrderCreated
auorderc = amazon_ups_pb2.AUOrderCreated()
auorderc.orderid = 2
auorderc.destinationx = 12
auorderc.destinationy = 13
auorderc.seqnum = 9

# generate AURequestTruck
aurt = amazon_ups_pb2.AURequestTruck()
aurt.whnum = 1
aurt.x = 122
aurt.y = 321
aurt.seqnum = 10

# generate AUOrderLoaded 
auol = amazon_ups_pb2.AUOrderLoaded()
auol.orderid = 2
auol.truckid = 3
auol.packageid = 678
auol.description = "test pack"
auol.seqnum = 11

auc.ordercreated = auorderc


print("sending message to ups ...")
send_message_to_ups(accept_socket, auc)





    

