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
from upsserver import *
def amazon_server():
    try:
        print("dock to frontend")
        ip_port_frontend = ('0.0.0.0', 8888)
        s_to_frontend = socket.socket()
        s_to_frontend.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s_to_frontend.bind(ip_port_frontend)
        s_to_frontend.listen(5)
        while True:
            frontend, _ = s_to_frontend.accept()
            message, yes=recv_msg(s_to_frontend)
            uaconnected_to_world=protocol_buffer.to_UAConnectedToWorld(1,1)
            uacommands=amazon_ups_pb2.UACommands()
            uacommands.connectedtoworld=uaconnected_to_world
            send_message_to_amazon_and_check_ack(frontend,uacommands)
            print(message)
            break
    except Exception as ex:
        print(ex)