#include "server.h"


#include "socket.h"
#include "myException.h"
#include "processFunction.h"
#include "sqlOperation.h"


connection * Server::connectDB(string dbName, string userName, string password) {
   //connection * C = new connection("dbname=" + dbName + " user=" + userName + " password=" + password);  
   connection * C = new connection("host=db port=5432 dbname=" + dbName + " user=" + userName +
                                   " password=" + password);  // use in docker
  if (!C->is_open()) {
    throw MyException("Cannot open database.");
  }
  return C;
}


void Server::disConnectDB(connection * C) {
  C->disconnect();
}


Server::Server() :
  whNum(5), worldHost("vcm-30499.vm.duke.edu"), worldPort("23456"),
  worldID(), upsPort("9090"), webPort("8888"),
  seqNum(0)
{
    cout << "Constructing server" << endl;
    //connection * C = new connection("dbname=mini_amazon user=postgres password=abcdef123 port=5432");  //used it no docker
    connection * C =new connection("host=db port=5432 dbname= mini_amazon user= postgres password= abcdef123");  // use in docker   
    if (!C->is_open()) {
      throw MyException("Cannot open database.");
    }
    //dropAllTable(C);
    //createTable(C, "./database/tables.sql");
    //insertSampleData(C);  //for testing
    C->disconnect();
    
    for (size_t i = 0; i < 65536; ++i) {
      seqNumTable.emplace_back(false);
    }
}

Server & Server::getInstance() {
    static Server s;
    return s;
}

/*
  init gpb buffer ptrs
*/
void Server::initializeWorldCommunication() {
  worldReader = make_unique<gpbIn>(worldFD);
  worldWriter = make_unique<gpbOut>(worldFD);
}

void Server::initializeUpsCommunication() {
  upsReader = make_unique<gpbIn>(upsFD);
  upsWriter = make_unique<gpbOut>(upsFD);
}

/*
  connect to world
*/
void Server::initAconnect(AConnect & aconnect) {
  //init initwh
  for (int i = 0; i < whNum; ++i) {
    AInitWarehouse * w = aconnect.add_initwh();
    w->set_id(i);
    w->set_x(i);
    w->set_y(i);
    whs.push_back(Warehouse(i, i, i));
  }
  //init isAmazon
  aconnect.set_isamazon(true);
}

void Server::AWHandshake(AConnect & aconnect, AConnected & aconnected) {
  //send AConnect 
  if (!sendMesgTo<AConnect>(aconnect, worldWriter.get())) {
    throw MyException("Cannot send AConnect command to world.");
  }
  //receive AConnected 
  if (!recvMesgFrom<AConnected>(aconnected, worldReader.get())) {
    throw MyException("Cannot recv AConnected command from world.");
  }
  //check AConnected
  if (aconnected.result() != "connected!") {
    throw MyException("Amazon-World handshake failed.");
  }
}

void Server::connectWorld() {
  //conncect to world
  worldFD = socketConnect(worldHost, worldPort);
  initializeWorldCommunication();
  //init Aconnect
  AConnect aconnect;
  initAconnect(aconnect);
  //Amazon-World handshake
  AConnected aconnected;
  AWHandshake(aconnect, aconnected);
  worldID = aconnected.worldid();
  cout << "Successfully connecting to world " << endl;
}

/*     
  connect to ups           
*/
void Server::initAUConnectCommand(AUCommands & aucommand) {
  //init AUConnectedToWorld
  AUConnectedToWorld * auconnect = aucommand.add_connectedtoworld();
  auconnect->set_worldid(worldID);
  size_t seqNum = requireSeqNum();
  cout << "**<seqNum used>** AUConnectedToWorld: " << seqNum << endl;
  auconnect->set_seqnum(seqNum);
}

void Server::connectUps() {  
  int serverFD = buildServer(upsPort);
  string clientIP;
  upsFD = serverAccept(serverFD, clientIP);
  initializeUpsCommunication();
  //init AUCommands
  AUCommands aucommand;
  initAUConnectCommand(aucommand);
  //push aucmd to upsQueue
  upsQueue.push(aucommand);
}

/*
  handle send/revc gpb cmds
*/
void Server::processReceivedWorldMessages() {
  while(true) {
    AResponses ar;
    cout << "---- start receving AResponses ------" << endl;
    if (!recvMesgFrom<AResponses>(ar, worldReader.get())) {
      continue;
    }
    cout << ar.DebugString() << endl;
    cout << "---- finish receving AResponses ------" << endl;
    AResponseHandler handler(ar);
    //handler.printAResponse();
    handler.handle();
  }
}

void Server::processReceivedUpsMessages() {
  while(true) {
    UACommands ar;
    cout << "---- start receving UACommands ------" << endl;
    if (!recvMesgFrom<UACommands>(ar, upsReader.get())) {
      continue;
    }
    cout << ar.DebugString() << endl;
    cout << "---- finish receving UACommands ------" << endl;
    AUResponseHandler handler(ar);
    //handler.printAUResponse();
    handler.handle();
  }
}

void Server::sendMessagesToWorld() {
  while(true) {
    ACommands msg;
    worldQueue.pop(msg);
    printAMessage(msg);
    if (!sendMesgTo<ACommands>(msg, worldWriter.get())) {
      throw MyException("fail to send message in world.");
    }
    cout << "---- finish sending ACommands ------" << endl;
  }

}

void Server::sendMessagesToUps() {
  while(true) {
    AUCommands msg;
    upsQueue.pop(msg);
    printAUMessage(msg);
    if (!sendMesgTo<AUCommands>(msg, upsWriter.get())) {
      throw MyException("fail to send message in ups.");
    }
    cout << "---- finish sending AUCommands ------" << endl;
  }
}

/*
  msg log
*/
void Server::printAUMessage(const AUCommands & msg) {
    cout << "---- start sending AUCommands ------" << endl;
    cout << msg.DebugString() << endl;    
}

void Server::printAMessage(const ACommands & msg) {
    cout << "---- start sending ACommands ------" << endl;
    cout << msg.DebugString() << endl;
}

/*
  seqNum counter
*/
size_t Server::requireSeqNum() {
  lock_guard<mutex> lck(seqNum_lock);
  size_t num = seqNum;
  ++seqNum;
  return num;
}

/*
  Web communication
*/
void Server::processOrderFromWeb(const int serverFD) {
    // wait to accept connection.
    cout << "waiting for order from web.." << endl;
    while(true) {
      int webFD;
      string clientIP;
      string msg;
      try {
        webFD = serverAccept(serverFD, clientIP);
        msg = recvMsg(webFD);
        thread t(processOrder, msg, webFD);
        t.detach();
      }
      catch (const std::exception & e) {
        std::cerr << e.what() << '\n';
      }
    }
    cout << "finish process Order From Web"<<endl;
}

void Server::run() {
  try{
    connectWorld();
    connectUps();
 
    thread recvWorldThread(&Server::processReceivedWorldMessages, this);
    recvWorldThread.detach();
    thread recvUpsThread(&Server::processReceivedUpsMessages, this);
    recvUpsThread.detach();
    thread sendWorldThread(&Server::sendMessagesToWorld, this);
    sendWorldThread.detach();
    thread sendUpsThread(&Server::sendMessagesToUps, this);
    sendUpsThread.detach();

    int serverFD = buildServer(webPort);
    processOrderFromWeb(serverFD);
  }
  catch (const std::exception & e) {
    cerr << e.what() << endl;;
    close(upsFD);
    close(worldFD);
    return;
  }
}