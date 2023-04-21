//for database querys, update the database;
#include <pqxx/pqxx>

void addTruck(connection *C);

void updateTruckStatus(connection *C, int truckid);

void getTruckStatus(connection *C, int truckid);


