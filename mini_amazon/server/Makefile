GDB = -g
THREAD = -pthread
PQXX = -lpqxx -lpq
GPB = `pkg-config --cflags --libs protobuf`
PROTO_CC = lib/build/gen/world_amazon.pb.cc lib/build/gen/amazon_ups.pb.cc
PROTO_H = lib/build/gen/world_amazon.pb.h lib/build/gen/amazon_ups.pb.h
VERSION = -std=c++17
TOOLS_H =  myException.h socket.h gpbCommunication.h msgQueue.h sqlOperation.h processFunction.h AResponseHandler.h AUResponseHandler.h
TOOLS_CPP = socket.cpp sqlOperation.cpp processFunction.cpp AResponseHandler.cpp AUResponseHandler.cpp
DATA_STRUCTURE_H = warehouse.h 

all: server

server: main.cpp server.cpp $(TOOLS_CPP) $(TOOLS_H) $(DATA_STRUCTURE_H) server.h $(PROTO_CC) $(PROTO_H)
	g++ -o server main.cpp server.cpp $(TOOLS_CPP) $(PROTO_CC) $(PQXX) $(GDB) $(THREAD) $(GPB) $(VERSION)

.PHONY: clean
clean:
	rm -rf *.o server
