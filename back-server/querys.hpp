//for database querys, update the database;
#include <iostream>
#include <pqxx/pqxx>
#include <string>
#include <cstdlib>
#include <fstream>
#include <ostream>
#include <sstream>

using namespace std;
using namespace pqxx;

void addTruck(connection *C, int x, int y, string status);

void addOrder(connection *C, int orderId, string upsaccout, int dest_x, int dest_y);

void addDelivery(connection *C, int orderId, int packageId, int dest_x, int dest_y, int truckId, string status);

void updateTruckStatus(connection *C, int truckId, string status);

void updateDeliveryStatus(connection *C, int packageId, string status);

void updateDeliveryAddress(connection *C, int packageId, int dest_x, int dest_y);

void getTruckDelivery(connection *C, int truckId);

void getTruckStatus(connection *C, int truckid);


