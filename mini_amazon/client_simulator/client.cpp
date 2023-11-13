#include "socket.h"

int main() {


    string host = "vcm-30541.vm.duke.edu";
    string port = "8888";

    // Connect to the server
    int socket_fd;
    while(1){
        try{
            socket_fd = socketConnect(host, port);
            break;
        }
        catch(exception & e){
            //printf("trying again to connect with world");
            sleep(2);
        }     
    }
    // int socket_fd = socketConnect(host, port);
    // if (socket_fd == -1) {
    //     cerr << "Failed to connect to the server." << endl;
    //     return 1;
    // }

    // Send an orderID as a message
    string orderID = "1";
    sendMsg(socket_fd, orderID.c_str(), sizeof(orderID));
    string res = recvMsg(socket_fd);
    cout << "recv: "<< res << endl;
    // Close the socket
    close(socket_fd);

    return 0;
}
