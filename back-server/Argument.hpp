#include <stdlib.h>

class Argument {
 private:
  int world_socket;
  int amazon_socket;
 public:
  Argument(int world_socket,int amazon_socket){
    this->world_socket=world_socket;
    this->amazon_socket=amazon_socket;
  };
  ~Argument();
  int getWorldSocket(){
    return world_socket;
  }
  int getAmazonSocket(){
    return amazon_socket;
  }
};