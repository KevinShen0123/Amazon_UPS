#include "processFunction.h"
#include "sqlOperation.h"
#include "warehouse.h"
#include "server.h"
#include "socket.h"
#include "myException.h"

#include <vector>
#include <string>
#include <random>
/*
  randomly select a warehouse
*/
int selectWareHouse(const vector<Warehouse> &whList) {
  std::random_device rd;
  std::mt19937 gen(rd());
  std::uniform_int_distribution<> distrib(0, whList.size() - 1);
  int index = distrib(gen);
  return index;
}

void processOrder(string msg, int webID) {
  unique_ptr<connection> C(Server::connectDB("mini_amazon", "postgres", "abcdef123"));
  cout << "successfully receive order request, begin processing it.." << endl;
  cout << "OrderID is: "<< msg <<endl;
  int orderID = stoi(msg);
  
  // determine to use which warehouse.
  Server & server = Server::getInstance();
  vector<Warehouse> whList = server.getWhs();
  int whIndex = selectWareHouse(whList);
  int whID = whList[whIndex].getID();
  setPackagesWhID(C.get(), orderID, whID);
  cout << "finishing selecting warehouse"<< endl;
  // send back ack info to front-end
  string ackResponse = "ACK";
  sendMsg(webID, ackResponse.c_str(), ackResponse.length());
  close(webID);
  cout << "finishing sending ACK to web"<< endl;
  // save order
  server.order_lck.lock();
  server.orderQueue.push(orderID);
  server.order_lck.unlock();

  // create APurchasemore command
  cout << "Starting create APurchasemore" << endl;
  ACommands ac;
  APurchaseMore * ap = ac.add_buy();
  ap->set_whnum(whID);
  vector<int> packageIDs = getPackageIDs(C.get(), orderID);
  // add seqNum
  size_t seqNum = server.requireSeqNum();
  cout << "**<seqNum used>** Apurchasemore: " << seqNum << endl;
  ap->set_seqnum(seqNum);
  for(auto packageID: packageIDs) {
    AProduct * aproduct = ap->add_things();
    aproduct->set_id(getPackageProductID(C.get(), packageID));
    aproduct->set_count(getPackageAmount(C.get(), packageID));
    aproduct->set_description(getPackageDesc(C.get(), packageID));
  }

  pushWorldQueue(ac);  
  Server::disConnectDB(C.get());
  cout << "Finishing receiving order request, begin processing it.." << endl;
}

/*
  Send APack command to world
*/
void packOrder(int orderID, int whID) {
  cout << "begin pack order " << orderID << endl;
  Server & server = Server::getInstance();
  unique_ptr<connection> C(Server::connectDB("mini_amazon", "postgres", "abcdef123"));

  // create Apack command
  ACommands acommand;
  vector<int> packageIDs = getPackageIDs(C.get(), orderID);
  for(auto packageID: packageIDs) {
    APack * apack = acommand.add_topack();
    apack->set_whnum(whID);
    apack->set_shipid(packageID);
    AProduct * aproduct = apack->add_things();
    aproduct->set_id(getPackageProductID(C.get(), packageID));
    aproduct->set_count(getPackageAmount(C.get(), packageID));
    aproduct->set_description(getPackageDesc(C.get(), packageID));
    // add seqNum to this command.
    size_t seqNum_apack = server.requireSeqNum();
    cout << "**<seqNum used>** APack: " << seqNum_apack << endl;
    apack->set_seqnum(seqNum_apack);
  }
  cout << "inside packOrder :" << acommand.DebugString() << endl;
  
  pushWorldQueue(acommand);
  Server::disConnectDB(C.get());
  cout << "Successfully send Apack command to world." << endl; 
}

/*
  Send AUOrderCreated and AURequestTruck command to UPS 
*/
void requestTruck(int orderID, int whID) {
  cout << "begin call a truck for order " << orderID << endl;
  unique_ptr<connection> C(Server::connectDB("mini_amazon", "postgres", "abcdef123"));
  Server & server = Server::getInstance();

  // get warehouse information
  int wh_x = -1;
  int wh_y = -1;
  vector<Warehouse> whList = server.getWhs();
  for (auto wh : whList) {
    if (wh.getID() == whID) {
      wh_x = wh.getX();
      wh_y = wh.getY();
      break;
    }
  }
  AUCommands aucommand;
  //create AUOrderCreated Command
  AUOrderCreated * auordercreated = aucommand.add_ordercreated();
  auordercreated->set_orderid(orderID);
  auordercreated->set_destinationx(getOrderAddrx(C.get(), orderID));
  auordercreated->set_destinationy(getOrderAddry(C.get(), orderID));
  auordercreated->set_upsaccount(getOrderUPSID(C.get(),orderID)); //optional
  int seqNum_auordercreated = server.requireSeqNum();
  cout << "**<seqNum used>** auordercreated: " << seqNum_auordercreated << endl;
  auordercreated->set_seqnum(seqNum_auordercreated);
  //create AOrderATruck Command
  AURequestTruck * aurequesttruck = aucommand.add_requesttruck();
  aurequesttruck->set_whnum(whID);
  aurequesttruck->set_x(wh_x);
  aurequesttruck->set_y(wh_y);
  int seqNum_aurequesttruck = server.requireSeqNum();
  cout << "**<seqNum used>** aurequesttruck: " << seqNum_aurequesttruck << endl;
  aurequesttruck->set_seqnum(seqNum_aurequesttruck);

  pushUpsQueue(aucommand);
  Server::disConnectDB(C.get());
  cout << "Successfully send AOrderATruck command to UPS." << endl;; 
}

/* ------------------------ "Message Queue functions" ------------------------ */

void pushUpsQueue(AUCommands& aucommand) {
  Server &server = Server::getInstance();
  bool all_ack_received = false;

  while (!all_ack_received) {
    all_ack_received = true;

    // check AUConnectedToWorld 
    for (int i = 0; i < aucommand.connectedtoworld_size(); ++i) {
      AUConnectedToWorld *cmd = aucommand.mutable_connectedtoworld(i);
      int seqNum = cmd->seqnum();
      if (server.seqNumTable[seqNum]) {
        aucommand.mutable_connectedtoworld()->DeleteSubrange(i, 1);
        --i;
      } else {
        all_ack_received = false;
      }
    }

    // check AUOrderCreated 
    for (int i = 0; i < aucommand.ordercreated_size(); ++i) {
      AUOrderCreated *cmd = aucommand.mutable_ordercreated(i);
      int seqNum = cmd->seqnum();
      if (server.seqNumTable[seqNum]) {
        aucommand.mutable_ordercreated()->DeleteSubrange(i, 1);
        --i;
      } else {
        all_ack_received = false;
      }
    }

    // check AURequestTruck 
    for (int i = 0; i < aucommand.requesttruck_size(); ++i) {
      AURequestTruck *cmd = aucommand.mutable_requesttruck(i);
      int seqNum = cmd->seqnum();
      if (server.seqNumTable[seqNum]) {
        aucommand.mutable_requesttruck()->DeleteSubrange(i, 1);
        --i;
      } else {
        all_ack_received = false;
      }
    }

    // check AUOrderLoaded 
    for (int i = 0; i < aucommand.orderloaded_size(); ++i) {
      AUOrderLoaded *cmd = aucommand.mutable_orderloaded(i);
      int seqNum = cmd->seqnum();
      if (server.seqNumTable[seqNum]) {
        aucommand.mutable_orderloaded()->DeleteSubrange(i, 1);
        --i;
      } else {
        all_ack_received = false;
      }
    }

    // check Err 
    for (int i = 0; i < aucommand.error_size(); ++i) {
      Err *cmd = aucommand.mutable_error(i);
      int seqNum = cmd->seqnum();
      if (server.seqNumTable[seqNum]) {
        aucommand.mutable_error()->DeleteSubrange(i, 1);
        --i;
      } else {
        all_ack_received = false;
      }
    }

    // push AUCommands to upsQueue（if there is unACKed command）
    if (!all_ack_received) {
      server.upsQueue.push(aucommand);
    }
    std::this_thread::sleep_for(std::chrono::milliseconds(1000));
  }
}

void pushWorldQueue(ACommands& acommand) {
  Server &server = Server::getInstance();
  bool all_ack_received = false;

  while (!all_ack_received) {
    all_ack_received = true;

    // check APurchaseMore 
    for (int i = 0; i < acommand.buy_size(); ++i) {
      APurchaseMore *cmd = acommand.mutable_buy(i);
      int seqNum = cmd->seqnum();
      if (server.seqNumTable[seqNum]) {
        acommand.mutable_buy()->DeleteSubrange(i, 1);
        --i;
      } else {
        all_ack_received = false;
      }
    }

    // check APack 
    for (int i = 0; i < acommand.topack_size(); ++i) {
      APack *cmd = acommand.mutable_topack(i);
      int seqNum = cmd->seqnum();
      if (server.seqNumTable[seqNum]) {
        acommand.mutable_topack()->DeleteSubrange(i, 1);
        --i;
      } else {
        all_ack_received = false;
      }
    }

    // check APutOnTruck 
    for (int i = 0; i < acommand.load_size(); ++i) {
      APutOnTruck *cmd = acommand.mutable_load(i);
      int seqNum = cmd->seqnum();
      if (server.seqNumTable[seqNum]) {
        acommand.mutable_load()->DeleteSubrange(i, 1);
        --i;
      } else {
        all_ack_received = false;
      }
    }

    // check AQuery 
    for (int i = 0; i < acommand.queries_size(); ++i) {
      AQuery *cmd = acommand.mutable_queries(i);
      int seqNum = cmd->seqnum();
      if (server.seqNumTable[seqNum]) {
        acommand.mutable_queries()->DeleteSubrange(i, 1);
        --i;
      } else {
        all_ack_received = false;
      }
    }

    // push AUCommands to worldQueue(if there is unACKed command）
    if (!all_ack_received) {
      server.worldQueue.push(acommand);
    }
    std::this_thread::sleep_for(std::chrono::milliseconds(1000));
  }
}

/* ------------------------ "Process message from World" ------------------------ */

void processPurchaseMore(const APurchaseMore & r) {
  cout << "Begin handling AResponse: APurchaseMore "<< endl;
  int whID = r.whnum();
  // process saved order
  Server & server = Server::getInstance();
  server.order_lck.lock();
  int orderID = server.orderQueue.front();
  server.orderQueue.pop();
  server.order_lck.unlock();

  thread t1(packOrder,orderID, whID);
  t1.detach();
  thread t2(requestTruck,orderID, whID);
  t2.detach();
}

void processPacked(const APacked & r) {
  cout << "Begin handling AResponse: apackeds "<< endl;
  unique_ptr<connection> C(Server::connectDB("mini_amazon", "postgres", "abcdef123"));
  int packageId = r.shipid();
  updatepackPacked(C.get(), packageId);
  cout << "Already pack order " << packageId << endl;
  Server::disConnectDB(C.get());
}

void processLoaded(const ALoaded & r) {
  cout << "Begin handling AResponse: aloadeds "<< endl;
  unique_ptr<connection> C(Server::connectDB("mini_amazon", "postgres", "abcdef123"));

  int packageId = r.shipid();
  updatepackLoaded(C.get(), packageId);
  cout << "loaded order " << packageId << endl;

  // create orderloaded: contain truckid, packageid
  AUCommands aucommand;
  AUOrderLoaded * auOrderLoaded = aucommand.add_orderloaded();
  auOrderLoaded->set_packageid(packageId);
  auOrderLoaded->set_orderid(getPackageOrderID(C.get(), packageId));
  auOrderLoaded->set_truckid(getPackageUpsID(C.get(), packageId));
  auOrderLoaded->set_description(getPackageDesc(C.get(), packageId));
  // add seqNum to this command.
  Server & server = Server::getInstance();
  size_t seqNum = server.requireSeqNum();
  cout << "**<seqNum used>** orderloaded: " << seqNum << endl;
  auOrderLoaded->set_seqnum(seqNum);

  pushUpsQueue(aucommand);
  updatepackDelivering(C.get(), packageId);
  cout << "start deliver order " << packageId << endl;
  Server::disConnectDB(C.get());
}

/* ------------------------ "Process massages from UPS" ------------------------ */

void processUAConnectedToWorld(const UAConnectedToWorld & r) {
  cout << "Begin handling UAResponse: UAConnectedToWorld "<< endl;
  Server & server = Server::getInstance();
  if(r.worldid() != server.getWorldID()) {
    throw MyException("Error: Fail to connect to the same world");
  }
}

void processUADestinationUpdated(const UADestinationUpdated & r) {
  cout << "Begin handling UAResponse: UADestinationUpdated "<< endl;
  unique_ptr<connection> C(Server::connectDB("mini_amazon", "postgres", "abcdef123"));
  //change this order address
  int orderID = r.orderid();
  int new_x = r.destinationx();
  int new_y = r.destinationy();
  updateOrderAddr(C.get(), orderID, new_x, new_y);
  cout << "Updated order address to (" << new_x << ", " << new_y << ")" << endl;
  Server::disConnectDB(C.get());
}

void processUATruckArrived(const UATruckArrived & r) {
  cout << "Begin handling UAResponse: UATruckArrived "<< endl;
  unique_ptr<connection> C(Server::connectDB("mini_amazon", "postgres", "abcdef123"));

  //gettruck id and warehouse id
  int truckId = r.truckid();
  int whId = r.whnum();
  setOrderUpsID(C.get(), whId, truckId);
  cout << "Truck "<<truckId<<" arrived " << endl;
  
  // Get packed packages id
  vector<int> packedPackageIDs;
  while (packedPackageIDs.empty()) {
    packedPackageIDs = getPackedPackageIDs(C.get(), whId);
    if (packedPackageIDs.empty()) {
      // Wait for 1 second if the list is still empty
      std::this_thread::sleep_for(std::chrono::seconds(1));
    }
  }
  //create APutOnTruck Command
  cout << "start load order "<< endl;
  ACommands acommand;
  Server & server = Server::getInstance();
  for(const auto packedPackageID: packedPackageIDs) {
    APutOnTruck * aPutOnTruck = acommand.add_load();
    aPutOnTruck->set_whnum(whId);
    aPutOnTruck->set_shipid(packedPackageID);
    aPutOnTruck->set_truckid(truckId);
    size_t seqNum = server.requireSeqNum();
    cout << "**<seqNum used>** APutOnTruck: " << seqNum << endl;
    aPutOnTruck->set_seqnum(seqNum);
    updatepackLoading(C.get(), packedPackageID);
  }
  // add seqNum to this command.
  Server::disConnectDB(C.get());
  pushWorldQueue(acommand);
}

void processUAOrderDeparture(const UAOrderDeparture & r) {
  cout << "Begin handling UAResponse: UAOrderDeparture "<< endl;
  unique_ptr<connection> C(Server::connectDB("mini_amazon", "postgres", "abcdef123"));
  int packageId = r.packageid();
  updatepackDelivering(C.get(), packageId);
  cout << "Delivering package " << packageId << endl;

  Server::disConnectDB(C.get());
}

void processUAOrderDelivered(const UAOrderDelivered & r) {
  cout << "Begin handling UAResponse: UAOrderDelivered "<< endl;
  unique_ptr<connection> C(Server::connectDB("mini_amazon", "postgres", "abcdef123"));
  int packageId = r.packageid();
  updatepackDelivered(C.get(), packageId);
  cout << "Already delivered order " << packageId <<" with seqNum: "<<r.seqnum()<< endl;

  Server::disConnectDB(C.get());
}
