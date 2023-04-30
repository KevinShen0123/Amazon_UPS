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
#from upsserver import database_connection

def addTruck(connect, truckId, x, y, t_status):
    try:
        cur = connect.cursor()
        sql = "INSERT INTO TRUCK (TRUCK_ID, X, Y, T_STATUS) VALUES (" + str(truckId) + "," + str(x) + "," + str(
            y) + ",'" + t_status + "');"
        print("addtruck: " + sql)
        cur.execute(sql)
    except:
        pass
    connect.commit()
    # connect.close()

def addOrder(connect, orderId, upsaccount, dest_x, dest_y):
    try:
        cur = connect.cursor()
        sql = "INSERT INTO ORDERS (ORDER_ID, UPSACCOUNT, DEST_X, DEST_Y) VALUES (" + str(
            orderId) + ",'" + upsaccount + "'," + str(dest_x) + "," + str(dest_y) + ");"
        print("addorder: " + sql)
        print("add order is called!!!")
        cur.execute(sql)
    except:
        pass
    connect.commit()
    # connect.close()
def addDelivery(connect, packageId, orderId, truckId, dest_x, dest_y, description, d_status):
        cur = connect.cursor()
        sql = "INSERT INTO DELIVERY (PACKAGE_ID, ORDER_ID, TRUCK_ID, DEST_X, DEST_Y, DESCR, D_STATUS) VALUES ("
        sql+=str(packageId) + "," + str(orderId) + "," + str(truckId) + "," + str(dest_x) + "," + str(
            dest_y) + ",'" + str(description) + "','" + str(d_status) + "');"
        print("adddelivery: " + sql)
        cur.execute(sql)
        connect.commit()
def updateTruckStatus(connect, truckId, status):
    cur = connect.cursor()
    sql = "UPDATE TRUCK SET T_STATUS = "+"'"+status+"' WHERE TRUCK_ID="+str(truckId)+";"
    
    print("updateTruck: "+sql)
    cur.execute(sql)
    connect.commit()
def updateDeliveryStatus(connect, packageId, status):
    cur = connect.cursor()
    sql = "UPDATE DELIVERY SET D_STATUS = "+"'"+status+"' WHERE PACKAGE_ID="+str(packageId)+";"
    print("updateDelivery: "+sql)
    cur.execute(sql)
    connect.commit()
def updateDeliveryAddr(connect, packageId, dest_x, dest_y):
    cur = connect.cursor()
    sql_delivery = "UPDATE DELIVERY SET DEST_X ="+str(dest_x)+" ,DEST_Y="+str(dest_y)+" WHERE PACKAGE_ID="+str(packageId)+";"
    cur.execute(sql_delivery)
    print("updateDelivery: "+sql_delivery)

    sql_order = "UPDATE UPS_ORDER SET DEST_X ="+str(dest_x)+" ,DEST_Y="+str(dest_y)+" WHERE PACKAGE_ID="+str(packageId)+";"
    cur.execute(sql_order)
    print("updateDelivery: "+sql_order)
    
    cur.execute(sql_delivery)
    connect.commit()
# return incomplete delivery for the truck
def getCurrDelivery(connect, truckId):
    cur = connect.cursor()
    sql = "SELECT * FROM DELIVERY WHERE TRUCK_ID = "+str(truckId)+" AND D_STATUS <> "+"'deliveried';"
    print("selectDelivery: "+sql)
    cur.execute(sql)
    rows = cur.fetchall()
    connect.commit()
    return rows

# return truck status
def getTruckStatus(connect, truckId):
    cur = connect.cursor()
    sql = "SELECT T_STATUS FROM TRUCK WHERE TRUCK_ID = "+str(truckId)+";"
    print("selectTruckStatus: "+sql)
    cur.execute(sql)
    rows = cur.fetchall()
    # connect.close()
    connect.commit()
    return rows
def get_order(connect,order_id):
    cur = connect.cursor()
    sql = "SELECT * FROM ORDERS WHERE ORDER_ID = " + str(order_id) + ";"
    print("selectTruckStatus: " + sql)
    cur.execute(sql)
    rows = cur.fetchall()
    # connect.close()
    connect.commit()
    return rows
def add_warehouse(connect,Xcor,Ycor,WHID):
    try:
        xcorstr = str(Xcor)
        cur = connect.cursor()
        sql = "INSERT INTO WAREHOUSE(X,Y,WHID) VALUES"
        sql += "("
        sql += xcorstr
        sql += ","
        sql += str(Ycor)
        sql += ","
        sql += str(WHID)
        sql += ")"
        print("addwarehouse: " + sql)
        cur.execute(sql)
    except:
        pass
    connect.commit()
def get_warehouse_id(connect, x,y):
    cur = connect.cursor()
    sql="SELECT WHID FROM WAREHOUSE WHERE X="
    sql+=str(x)
    sql+=" AND Y="
    sql+=str(y)
    sql+=";"
    print("selectwarehouse: " + sql)
    cur.execute(sql)
    rows = cur.fetchall()
    # connect.close()
    connect.commit()
    return rows
def get_delivery(connect,packageid):
    cur = connect.cursor()
    sql = "SELECT * FROM DELIVERY WHERE PACKAGE_ID = " + str(packageid) + " AND D_STATUS <> " + "'deliveried';"
    print("selectDelivery: " + sql)
    cur.execute(sql)
    rows = cur.fetchall()
    # connect.close()
    connect.commit()
    return rows
def add_order_status(connect,order_id,od_status):
    cur = connect.cursor()
    sql = "INSERT INTO ORDER_STATUS (ORDER_ID, OD_STATUS, M_TIME) VALUES (" + str(order_id) + ",'" + str(
        od_status) + "'," + "NOW());"
    print("selectDelivery: " + sql)
    cur.execute(sql)
    connect.commit()
    return True
def get_delivery_orderid(connect,packageid):
    cur = connect.cursor()
    sql = "SELECT ORDER_ID FROM DELIVERY WHERE PACKAGE_ID = " + str(packageid) + ";"
    print("selectDelivery: " + sql)
    cur.execute(sql)
    rows = cur.fetchall()
    # connect.close()
    connect.commit()
    return rows
