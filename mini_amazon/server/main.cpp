#include "server.h"

int main() {
    GOOGLE_PROTOBUF_VERIFY_VERSION;
    Server & s = Server::getInstance();
    s.run();
    return 0;
}