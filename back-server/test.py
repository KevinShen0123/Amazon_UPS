import world_ups_pb2
import django
import os

import sys
from concurrent.futures import ThreadPoolExecutor
import socket
from threading import Thread
import threading
import time
from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _EncodeVarint
import world_ups_pb2 as World_UPS
from django.db.models import Q
from django.core.mail import EmailMultiAlternatives  # 这样可以发送HTML格式的内容了
from django.conf import settings  # 将settings的内容引进
def get_socket_to_world():
    world_host = '127.0.0.1'
    ip_port_w = (world_host, 12345)
    socket_to_world = socket.socket()
    try:
        socket_to_world.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        socket_to_world.connect(ip_port_w)
        print("connect to world" + "\n")
        return socket_to_world
    except:
        print("having problem in connectiong to world\n")
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
def recv_from_world(to_world_socket):
    whole_message, is_socket_closed = recv_msg(to_world_socket)
    if is_socket_closed:
        return None, True
    world_res = World_UPS.UConnected()
    try:
        world_res.ParseFromString(whole_message)
        print("------------------- recv from world -------------------")
        print(str(world_res))

        return world_res, False
    except:
        print("------------------- Error parsing message from world -------------------")
        return None, False
socket_to_world=get_socket_to_world()
uconnect=world_ups_pb2.UConnect()
uconnect.isAmazon=False
_EncodeVarint(socket_to_world.send, len(uconnect.SerializeToString()), None)
socket_to_world.send(uconnect.SerializeToString())
world_res,false=recv_from_world(socket_to_world)

