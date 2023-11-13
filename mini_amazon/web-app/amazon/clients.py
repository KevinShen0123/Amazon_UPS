
import socket
def confirm_order(order):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    client.connect(('vcm-30499.vm.duke.edu', 8888))

    orderInfo = str(order.order_id)

    try:       
        client.send(orderInfo.encode('utf-8'))
        
    except socket.error as e:
        print('Error sending data: %s' % e)

    print('after send')
    ACK_str = str(client.recv(1024))
