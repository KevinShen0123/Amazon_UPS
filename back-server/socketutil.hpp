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

using namespace std;
class Socket{
public:
    google::protobuf::io::FileOutputStream*world_socketstream;
	google::protobuf::io::FileOutputStream*amazon_socketstream;
	Socket(int world_socket,int amazon_socket){
		world_socketstream=new google::protobuf::io::FileOutputStream(world_socket);
		amazon_socketstream=new google::protobuf::io::FileOutputStream(amazon_socket);
	}
	Socket(){
		
	}
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

  cout << "Connecting to " << hostname << " on port " << port << "..." << endl;

  status = connect(socket_fd, host_info_list->ai_addr, host_info_list->ai_addrlen);
  if (status == -1) {
    std::cerr << "Error: cannot connect to socket" << std::endl;
    std::cerr << "  (" << hostname << "," << port << ")" << std::endl;
    exit(EXIT_FAILURE);
  }

  freeaddrinfo(host_info_list);
  return socket_fd;
}
template<typename T>
	bool sendMesgTo(const T & message,bool is_world) {
		//extra scope: make output go away before out->Flush()
		// We create a new coded stream for each message. Don’t worry, this is fast.
		if(is_world){
			   	google::protobuf::io::FileOutputStream*out=world_socketstream;
          		google::protobuf::io::CodedOutputStream output(out);
				// Write the size.
		const int size = message.ByteSize();
		output.WriteVarint32(size);
		uint8_t* buffer = output.GetDirectBufferForNBytesAndAdvance(size);
		if (buffer != NULL) {
		// Optimization: The message fits in one buffer, so use the faster
		// direct-to-array serialization path.
		message.SerializeWithCachedSizesToArray(buffer);;
		} 
		else{
			// Slightly-slower path when the message is multiple buffers.
			message.SerializeAsString();
		}
		if (output.HadError()) {
			delete out;
			return false;
		}
		out->Flush();
		std::cout<<"send finished!!!!!!!"<<out->GetErrno()<<std::endl;
		return true;
		}else{
			google::protobuf::io::FileOutputStream*out=amazon_socketstream;
			google::protobuf::io::CodedOutputStream output(out);
			// Write the size.
		const int size = message.ByteSize();
		output.WriteVarint32(size);
		uint8_t* buffer = output.GetDirectBufferForNBytesAndAdvance(size);
		if (buffer != NULL) {
		// Optimization: The message fits in one buffer, so use the faster
		// direct-to-array serialization path.
		message.SerializeWithCachedSizesToArray(buffer);;
		} 
		else{
			// Slightly-slower path when the message is multiple buffers.
			message.SerializeAsString();
		}
		if (output.HadError()) {
			delete out;
			return false;
		}
		out->Flush();
		std::cout<<"send finished!!!!!!!"<<out->GetErrno()<<std::endl;
		return true;
		}
	}
	template<typename T>
	bool recvMesgFrom(T & message,int fd){
		google::protobuf::io::FileInputStream * in = new google::protobuf::io::FileInputStream(fd);
		google::protobuf::io::CodedInputStream input(in);
		uint32_t size;
		if (!input.ReadVarint32(&size)) {
			delete in;
			return false;
		}
		// Tell the stream not to read beyond that size.
		google::protobuf::io::CodedInputStream::Limit limit = input.PushLimit(size);
		// Parse the message.
		if (!message.MergeFromCodedStream(&input)) {
			delete in;
			return false;
		}
		if (!input.ConsumedEntireMessage()) {
			delete in;
			return false;
		}
		// Release the limit.
		input.PopLimit(limit);
		return true;
	}
};