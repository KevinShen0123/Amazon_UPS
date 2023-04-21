#include  "querys.hpp"
#include "socketutil.hpp"
#include "bufferProcessing.hpp"
#include "world_ups.pb.h"
int main(){
    int world_socket=build_client("127.0.0.1","12345");
    std::vector<UInitTruck> us;
   UConnect uc=uConnect(false,1,us,false);
   std::string uconnectinfo=uc.SerializeAsString();
   int status=send(world_socket,uconnectinfo.c_str(),uconnectinfo.length(),0);
   if(status==-1){
    std::cerr<<"socket error!!!!!!"<<std::endl;
    exit(1);
   }
   char* world_message=new char[100];
   int recvstatus=recv(world_socket,world_message,100,0);
   std::string connectedMessage=std::string(world_message,100);
   UConnected ucd;
   ucd.ParseFromString(connectedMessage);
   std::cout<<"ucd world id: "<<ucd.worldid()<<"ucd result is: "<<ucd.result()<<std::endl;
}
