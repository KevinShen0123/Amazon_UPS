#ifndef _SQLOPERATION_H
#define _SQLOPERATION_H

#include "myException.h"

#include <fstream>
#include <iostream>
#include <pqxx/pqxx>
#include <string>


using namespace pqxx;
using namespace std;

void insertSampleData(connection* C);
void createTable(connection * C, const string fileName);
void dropAllTable(connection * C);

std::vector<std::string> getPackagesfOrder(connection * C, int order_id);
void purchaseProduct(connection * C, int package_id,int wh_id);
int getOrderAddrx(connection* C, int order_id);
int getOrderAddry(connection* C, int order_id);
vector<int> getPackageIDs(connection* C, int order_id);

int getPackageProductID(connection* C, int package_id);
string getPackageProductDesc(connection* C, int package_id);
string getOrderUPSID(connection* C, int order_id);
int getPackageOrderID(connection* C, int package_id);
int getPackageUpsID(connection* C, int package_id);
string getPackageDesc(connection* C, int package_id);
int getPackageAmount(connection* C, int package_id);
vector<int> getPackedPackageIDs(connection* C, int wh_id);

void setPackagesWhID(connection* C, int orderID, int whID);
void setOrderUpsID(connection *C, int wh_id, int ups_id);

void updateOrderAddr(connection* C, int orderID, int new_x, int new_y);
void updatepackPacking(connection* C, int package_id);
void updatepackPacked(connection * C, int package_id);
void updatepackLoading(connection * C, int package_id);
void updatepackLoaded(connection * C, int package_id);
void updatepackDelivering(connection * C, int package_id);
void updatepackDelivered(connection * C, int package_id);


#endif
