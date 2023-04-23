#include  "querys.hpp"
#include "socketutil.hpp"
#include "bufferProcessing.hpp"
#include "world_ups.pb.h"
#include "lib.h"

using namespace pqxx;

int connectToDatabase();

int connectToWorld(const char * hostname, const char * port, int worldId);

int connectToAmazon(const char * hostname, const char * port);

int connectToFrontend(const char * hostname, const char * port);

void* handleWorldConnection(void*);

void* handleAmazonConnection(void*);


void createTruck(vector<Truck> trucks);

void createOrder(AUOrderCreated auoc);

UGoPickup pickup(connection*C,AURequestTruck request, int world_socket,int amazon_socket);

void createDelivery(int order_id,int package_id,int truck_id);

UGoDeliver startDelivery(int order_id,int package_id,int truck_id,int world_socket,int amazon_socket);

UAOrderDelivered deliveryMade(UDeliveryMade udm);




