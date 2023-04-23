#include  "querys.hpp"
#include "bufferProcessing.hpp"
#include "world_ups.pb.h"
#include "Argument.hpp"
#include <pqxx/pqxx>
#include <stdlib.h>
#include "interact.hpp"
#include "amazon_ups.pb.h"
#include <sstream>
#include <vector>
using namespace std;
int curWorldId=-1;
connection *C;

int world_request_sequence_number=0;
pthread_mutex_t thread_lock;

void createTruck(vector<Truck> trucks){
	for (int i=0; i< (int)trucks.size(); i++) {
		addTruck(C, trucks[i].x, trucks[i].y, "idle");
	}
}

void createOrder(AUOrderCreated auoc){
	addOrder(C, auoc.orderid(), auoc.upsaccount(), auoc.destinationx(), auoc.destinationy());
}

UGoPickup pickup(AURequestTruck request, int world_socket){
  UGoPickup pick;
  work W(*C);
  std::stringstream sql;
  sql<<"SELECT id from Truck WHERE status="<<W.quote("idle")<<" OR status="<<W.quote("arrive warehouse")<<" OR status="<<W.quote("delivering")<<";";
  W.commit();
  nontransaction T(*C);
  result R(T.exec(sql.str()));
  int selected_truck_id=1;
  for (result::const_iterator c = R.begin(); c != R.end(); ++c) {
        selected_truck_id=c[0].as<int>();
        break;
  }
   pick.set_seqnum(world_request_sequence_number);
   pick.set_truckid(selected_truck_id);
   pick.set_whid(request.whnum());
   return pick;
}

void createDelivery(int order_id,int package_id,int truck_id){
  std::stringstream sql;
  sql<<"SELECT * FROM Order WHERE orderid="<<order_id<<";";
  nontransaction T(*C);
  result R(T.exec(sql.str()));
  int destx=0;
  int desty=0;
  for (result::const_iterator c = R.begin(); c != R.end(); ++c) {
      destx=c[2].as<int>();
      desty=c[3].as<int>();
  }
  std::stringstream sql2;
  work W(*C);
  sql2<<"INSERT INTO Delivery(order_id,package_id,dest_x,dest_y,truck_id,status) VALUES("<<order_id<<","<<package_id<<","<<destx<<","<<desty<<","<<truck_id<<","<<0<<";";
  W.exec(sql2.str());
}

UGoDeliver startDelivery(int order_id,int package_id,int truck_id,int world_socket,int amazon_socket){
  UDeliveryLocation location;
  location.set_packageid(package_id);
  std::stringstream sql;
  sql<<"SELECT * FROM Delivery WHERE order_id="<<order_id<<" AND package_id="<<package_id<<" AND truck_id="<<truck_id<<";";
  nontransaction T(*C);
  result R(T.exec(sql.str()));
  int destx=0;
  int desty=0;
  for (result::const_iterator c = R.begin(); c != R.end(); ++c) {
     destx=c[2].as<int>();
     desty=c[3].as<int>();
     break;
  }
  location.set_x(destx);
  location.set_y(desty);
  std::vector<UDeliveryLocation> locations;
  //updateDeliveryStatus()
 UGoDeliver go=uGoDeliver(truck_id,world_request_sequence_number,locations);
 return go;
}

UAOrderDelivered deliveryMade(UDeliveryMade udm){
	int pack_id = udm.packageid();
	
	updateDeliveryStatus(C, pack_id, "delivered");

	stringstream sql;
	sql<<"SELECT DEST_X, DEST_Y FROM Delivery WHERE PACKAGE_ID="<<pack_id<<";";
  nontransaction T(*C);
  result R(T.exec(sql.str()));
  int destx=0;
  int desty=0;
  for (result::const_iterator c = R.begin(); c != R.end(); ++c) {
     destx=c[0].as<int>();
     desty=c[1].as<int>();
     break;
  }
	UAOrderDelivered uaod = uAOrderDelivered(pack_id, destx, desty, world_request_sequence_number);
	return uaod;

}

int connectToDatabase(){
	try{
    C = new connection("dbname=mini_ups user=postgres password=20230101 host=127.0.0.1 port=5432");
    if (C->is_open()) {
      cout << "Opened database successfully: " << C->dbname() << endl;
    } else {
      cout << "Can't open database" << endl;
    
    }
  } catch (const std::exception &e){
    cerr << e.what() << std::endl;
	}
}

// create a new world, set worldId = -1
int connectToWorld(const char * hostname, const char * port, int worldId){
  Socket* s=new Socket();
	int wld_socket=s->build_client(hostname,port);	


	// generate UConnect
	std::vector<UInitTruck> us;
	bool hasWorldId = (worldId<0) ? false : true;
  UConnect uc=uConnect(hasWorldId, worldId , us , false);
  std::string uconnectinfo=uc.SerializeAsString();	

	// send UConnect to World
	int status=send(wld_socket, uconnectinfo.c_str(), uconnectinfo.length(), 0);
  if(status==-1){
    std::cerr<<"ERROR: Send UConnect Failed."<<std::endl;
    exit(1);
  }
  
	// recv UConnected from World
	char* world_message=new char[100];
  int recvstatus=recv(wld_socket,world_message,100,0);

  std::string connectedMessage=std::string(world_message,100);
  UConnected ucd;
  ucd.ParseFromString(connectedMessage);

	// set World Id
	worldId = ucd.worldid();

  std::cout<<"ucd world id: "<<ucd.worldid()<<", ucd result is: "<<ucd.result()<<std::endl;

	return wld_socket;
}

int connectToAmazon(const char * hostname, const char * port){
  Socket*s=new Socket();
	int amz_socket = s->build_client(hostname, port);
}

void connectToFrontend(){
	
	int status;
  int socket_fd; 
  struct addrinfo host_info;
  struct addrinfo *host_info_list;
  const char *hostname = NULL;  // local host
  const char *port     = "4444";

  memset(&host_info, 0, sizeof(host_info));

  host_info.ai_family   = AF_UNSPEC;
  host_info.ai_socktype = SOCK_STREAM;
  host_info.ai_flags    = AI_PASSIVE;

  status = getaddrinfo(hostname, port, &host_info, &host_info_list);
  
  if (status != 0) {
    cerr << "Error: cannot get address info for host" << endl;
    cerr << "  (" << hostname << "," << port << ")" << endl;
    exit(1);
  } 

	// initialize socket
  socket_fd = socket(host_info_list->ai_family, 
		     host_info_list->ai_socktype, 
		     host_info_list->ai_protocol);
  if (socket_fd == -1) {
    cerr << "Error: cannot create socket" << endl;
    cerr << "  (" << hostname << "," << port << ")" << endl;
    exit(1);
  } 

  int yes = 1;
  status = setsockopt(socket_fd, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof(int));

  status = bind(socket_fd, host_info_list->ai_addr, host_info_list->ai_addrlen);
  if (status == -1) {
    cerr << "Error: cannot bind socket" << endl;
    cerr << "  (" << hostname << "," << port << ")" << endl;
    exit(1);
  } 

  status = listen(socket_fd, 100);
  if (status == -1) {
    cerr << "Error: cannot listen on socket" << endl; 
    cerr << "  (" << hostname << "," << port << ")" << endl;
    exit(1);
  } 

	cout<<"Initialize the listen socket for the frontend"<<endl;

	while (true) {
    struct sockaddr_in socket_addr;
    socklen_t socket_addr_len = sizeof(socket_addr);

    // accept frontend connection
    int client_fd = accept(socket_fd, (struct sockaddr *)&socket_addr, &socket_addr_len);
    if (client_fd == -1) {
      std::cerr << "Error: cannot accept connection on socket" << std::endl;
      exit(EXIT_FAILURE);
    }

		cout<<"Connected to the frontend."<<endl;
		// pthread_t p;
    // Argument * args = new Argument(socket_fd, client_fd, tid, cache, log, client_ip);
    // pthread_create(&p, NULL, handleRequest, args);
	}

}

void* send_to_world(void* msgs){
  pthread_mutex_lock(&thread_lock);
  std::string* messages=(std::string *) msgs;
  int world_socket=atoi(messages[0].c_str());
  std::string message=messages[1];
  send(world_socket,message.c_str(),message.length(),0);
  pthread_mutex_unlock(&thread_lock);
}
void* send_to_amazon(void* msgs){
   pthread_mutex_lock(&thread_lock);
   std::string* messages=(std::string*)msgs;
   int amazon_socket=atoi(messages[0].c_str());
   std::string message=messages[1];
   send(amazon_socket,message.c_str(),message.length(),0);
   pthread_mutex_unlock(&thread_lock);
}
void* handleWorldConnection(void* arguments){
  Argument* args=(Argument*)arguments;
  int world_socket=args->getWorldSocket();
  int amazon_socket=args->getAmazonSocket();
  while(true){
     char* msg=new char[100];
     int status=recv(world_socket,msg,100,0);
     if(status==-1){
        std::cerr<<"world lost connection"<<std::endl;
        throw std::exception();
     }
     UResponses response;
     bool isResponse=response.ParseFromString(std::string(msg,status));
     if(isResponse==false){
      std::cerr<<"error happened"<<std::endl;
      break;
     }else{
       if(response.completions().size()>0){

       }
     }
  }
  return NULL;
}
void* handleAmazonConnection(void* arguments){
  Argument* args=(Argument*)arguments;
  int world_socket=args->getWorldSocket();
  int amazon_socket=args->getAmazonSocket();
  while(true){
    char* msg=new char[100];
    int status=recv(amazon_socket,msg,100,0);
    if(status==-1){
      std::cerr<<"amazon lost connection"<<std::endl;
      throw std::exception();
    }
    AUCommands commands;
    bool isAU=commands.ParseFromString(std::string(msg,status));
    if(isAU==false){
      std::cerr<<"error happend"<<std::endl;
      break;
    }else{
       if(commands.ordercreated().size()>0){
          //create all the orders in order created
       }
       if(commands.requesttruck().size()>0){
          for(int i=0;i<commands.requesttruck().size();i++){
            UGoPickup x=pickup(commands.requesttruck()[i],world_socket);
            pthread_t pickUpRequestThread;
            std::string msgs[2];
            std::stringstream s1;
            s1<<world_socket;
            msgs[0]=s1.str();
            msgs[1]=x.SerializeAsString();
            pthread_create(&pickUpRequestThread,NULL,send_to_world,(void*)msgs);
          }
       }
       if(commands.orderloaded_size()>0){
        for(int j=0;j<commands.orderloaded().size();j++){
          AUOrderLoaded x=commands.orderloaded()[j];
          UGoDeliver deliver=startDelivery(x.orderid(),x.truckid(),x.packageid(),world_socket,amazon_socket);
          pthread_t deliverRequestToWorld;
           std::string msgs[2];
            std::stringstream s1;
            s1<<world_socket;
            msgs[0]=s1.str();
            msgs[1]=deliver.SerializeAsString();
            pthread_create(&deliverRequestToWorld,NULL,send_to_world,(void*)msgs);
            UAOrderDeparture uaod;
            uaod.set_orderid(x.orderid());
            uaod.set_packageid(x.packageid());
            uaod.set_trackingnum(x.packageid());
            uaod.set_seqnum(world_request_sequence_number);
            pthread_t orderDeparture;
             std::string msgss[2];
            std::stringstream s2;
            s2<<world_socket;
            msgss[0]=s2.str();
            msgss[1]=uaod.SerializeAsString();
            pthread_create(&orderDeparture,NULL,send_to_amazon,(void*)msgss);
        }
       }
    }
    delete msg;
  }
  return NULL;
}

int main_func(int argc, char* argv[] ){
int createTruck(){

}

int createOrder(){

}

int deliveryMade(){
	
}


int main(int argc, char* argv[] ){

	if ( argc!=5 ) {
		cout<<"ERROR: Invalid Command Line Argument."<<endl;
		return EXIT_FAILURE;
	}

	const char* amz_ip = argv[1];
	const char* amz_port = argv[2];

	curWorldId = atoi(argv[3]);
	int truck_num = atoi(argv[4]);
	
	// connect to World
  int wld_socket = connectToWorld("127.0.0.1","12345", curWorldId);
  int amz_socket = connectToAmazon(amz_ip, amz_port);
	// initialize a thread to handle world connection
	pthread_t wld_thread;
  Argument * wld_arg1 =new Argument(wld_socket,amz_socket);
  pthread_create(&wld_thread, NULL, handleWorldConnection, wld_arg1);

	// connection to Amazon
	// initialize a thread to handle amazon connection
	pthread_t amz_thread;
  Argument * amz_args = new Argument(wld_socket,amz_socket);
  pthread_create(&amz_thread, NULL, handleAmazonConnection, amz_args);

	// recv AUOrderCreated from amazon
	// send UACommand ack

	// recv AURequestedTruck
	// send UACommand ack

	// send UATruckArrived
	// recv AUCommand ack

	// recv AUOrderLoaded
	// send UACommand ack

	// send UAOrderDeparture
	// recv AUCommand ack

	// send UAOrderDeliveried
	// recv AUCommand ack

	// recv 

  
	// connection to Frontend
	connectToFrontend();

}
int main(int argc, char**argv){ 
 UConnect*c=new UConnect();
c->set_isamazon(false);
Socket* s = new Socket();
int world_socket = s->build_client("127.0.0.1", "12345");
std::cout << "fault2" << std::endl;
google::protobuf::io::FileOutputStream* out = new google::protobuf::io::FileOutputStream(world_socket);
out->SetCloseOnDelete(false);
google::protobuf::io::CodedOutputStream output(out);
// Write the size.
const int size = c->ByteSize();
output.WriteVarint32(size);
if (!output.HadError()) {
  uint8_t* buffer = (uint8_t*) malloc(size);
  c->SerializeWithCachedSizesToArray(buffer);
  output.WriteRaw(buffer, size);
  free(buffer);
}
if (output.HadError()) {
  delete out;
  return false;
}
out->Flush();
std::cout << "send finished!!!!!!!" << out->GetErrno() << std::endl;
UConnected ud;
s->recvMesgFrom(ud, world_socket);
std::cout << "receive message success!!!!!!!" << std::endl;
std::cout << ud.worldid() << "  " << ud.result() << std::endl;
return 0;
}
