#include <stdlib.h>
#include <stdio.h>
#include <cstring>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <climits>
#include <ctime>
#include <error.h>
#include <mutex>
#include <netdb.h>
#include <netinet/in.h>
#include <unistd.h>
#include<pthread.h>
#include <exception>
int build_client(const char * hostname, const char * port) {
  struct addrinfo host_info;
  struct addrinfo * host_info_list;
  int socket_fd;
  int status;

  memset(&host_info, 0, sizeof(host_info));
  host_info.ai_family = AF_UNSPEC;
  host_info.ai_socktype = SOCK_STREAM;

  status = getaddrinfo(hostname, port, &host_info, &host_info_list);
  if (status != 0) {
    std::cerr << "Error: cannot get address info for host" << std::endl;
    std::cerr << "  (" << hostname << "," << port << ")" << std::endl;
    exit(EXIT_FAILURE);
  }

  socket_fd = socket(host_info_list->ai_family,
                     host_info_list->ai_socktype,
                     host_info_list->ai_protocol);
  if (socket_fd == -1) {
    std::cerr << "Error: cannot create socket" << std::endl;
    std::cerr << "  (" << hostname << "," << port << ")" << std::endl;
    exit(EXIT_FAILURE);
  }

  //cout << "Connecting to " << hostname << " on port " << port << "..." << endl;

  status = connect(socket_fd, host_info_list->ai_addr, host_info_list->ai_addrlen);
  if (status == -1) {
    std::cerr << "Error: cannot connect to socket" << std::endl;
    std::cerr << "  (" << hostname << "," << port << ")" << std::endl;
    exit(EXIT_FAILURE);
  }

  freeaddrinfo(host_info_list);
  return socket_fd;
}
void sendTo(int socket_fd,std::string msg){
    int status=send(socket_fd,msg.c_str(),msg.length(),0);
    if(status==-1){
        std::cerr<<"send error!!!!!!!"<<std::endl;
        throw std::exception();
    }
}
std::string recvFrom(int socket_fd,int length){
    char* recved=new char[length];
    int status=recv(socket_fd,recved,length,0);
    if(status==-1){
        std::cerr<<"received error!!!!!"<<std::endl;
        throw std::exception();
    }
    return std::string(recved,length);
}
