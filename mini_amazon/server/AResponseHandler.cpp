#include "AResponseHandler.h"
#include "processFunction.h"
#include "gpbCommunication.h"
#include "server.h"

AResponseHandler::AResponseHandler(const AResponses & r) {
  for (int i = 0; i < r.arrived_size(); i++) {
    apurchasemores.push_back(std::move(r.arrived(i)));
    seqNums.push_back(r.arrived(i).seqnum());
  }

  for (int i = 0; i < r.ready_size(); i++) {
    apackeds.push_back(std::move(r.ready(i)));
    seqNums.push_back(r.ready(i).seqnum());
  }

  for (int i = 0; i < r.loaded_size(); i++) {
    aloadeds.push_back(std::move(r.loaded(i)));
    seqNums.push_back(r.loaded(i).seqnum());
  }

  // record acks from world
  for (int i = 0; i < r.acks_size(); i++) {
    Server & server = Server::getInstance();
    server.seqNumTable[r.acks(i)] = true;
  }
}

bool AResponseHandler::requireWorldAckedSet(int seqNum) {
  Server & server = Server::getInstance();
  auto it = server.worldAckedSet.find(seqNum);

  if (it == server.worldAckedSet.end()) {
    server.worldAckedSet.insert(seqNum);
    return false;
  }
  else {
    return true;
  }
}

void AResponseHandler::handle() {
  ACommands ac;
  for (int i = 0; i < seqNums.size(); i++) {
    ac.add_acks(i);
    ac.set_acks(i, seqNums[i]);
  }
  Server & server = Server::getInstance();
  server.worldQueue.push(ac);

  for (auto r : apurchasemores) {
    if (requireWorldAckedSet(r.seqnum()) == false) {
      thread t(processPurchaseMore, r);
      t.detach();
    }
  }

  for (auto r : apackeds) {
    if (requireWorldAckedSet(r.seqnum()) == false) {
      thread t(processPacked, r);
      t.detach();
    }
  }

  for (auto r : aloadeds) {
    if (requireWorldAckedSet(r.seqnum()) == false) {
      thread t(processLoaded, r);
      t.detach();
    }
  }
}
