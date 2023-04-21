#include  "querys.hpp"
#include "socketutil.hpp"
#include "bufferProcessing.hpp"
#include "world_ups.pb.h"
#include "Argument.hpp"
#include <pqxx/pqxx>
#include <stdlib.h>

using namespace std;

int curWorldId=-1;
connection *C;

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
	int wld_socket=build_client(hostname,port);	


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
  int recvstatus=recv(world_socket,world_message,100,0);

  std::string connectedMessage=std::string(world_message,100);
  UConnected ucd;
  ucd.ParseFromString(connectedMessage);

	// set World Id
	worldId = ucd.worldid();

  std::cout<<"ucd world id: "<<ucd.worldid()<<", ucd result is: "<<ucd.result()<<std::endl;

	return wld_socket;
}


int connectToAmazon(const char * hostname, const char * port){
	int amz_socket = build_client(hostname, port);
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
	// initialize a thread to handle world connection
	pthread_t wld_thread;
  Argument * wld_args = new Argument(wld_socket);
  pthread_create(&wld_thread, NULL, handleWorldConnection, wld_args);

	// connection to Amazon
	int amz_socket = connectToAmazon(amz_ip, amz_port);
	// initialize a thread to handle amazon connection
	pthread_t amz_thread;
  Argument * amz_args = new Argument(amz_socket);
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
