#ifndef _PROCESSFUNCTION_H
#define _PROCESSFUNCTION_H

#include <vector>
#include <string>

#include "warehouse.h"
#include "lib/build/gen/world_amazon.pb.h"
#include "lib/build/gen/amazon_ups.pb.h"


void pushUpsQueue(AUCommands& aucommand);
void pushWorldQueue(ACommands& acommand);

int selectWareHouse(const vector<Warehouse> & whList);
void processOrder(string msg, int orderID); 
void packOrder(int orderID, int whID);
void requestTruck(int orderID, int whID);

//amazon-world
void processPurchaseMore(const APurchaseMore & r);
void processPacked(const APacked & r);
void processLoaded(const ALoaded & r);
//amazon-ups
void processUAConnectedToWorld(const UAConnectedToWorld & r);
void processUADestinationUpdated(const UADestinationUpdated & r);
void processUATruckArrived(const UATruckArrived & r);
void processUAOrderDeparture(const UAOrderDeparture & r);
void processUAOrderDelivered(const UAOrderDelivered & r);

#endif
