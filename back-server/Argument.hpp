#include <stdlib.h>

class Argument {
 private:
  int socket_fd;


 public:
  Argument(int sfd): socket_fd(sfd){};
  ~Argument();

  int getSocketFd(){ return socket_fd; }
};