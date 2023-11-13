#ifndef _SERVER_H
#define _SERVER_H

#include <pqxx/pqxx>
#include <iostream>
#include <string>
#include <thread>

#include "warehouse.h"
#include "gpbCommunication.h"
#include "AResponseHandler.h"
#include "AUResponseHandler.h"
#include "msgQueue.h"

using namespace std;
using namespace pqxx;


class Server {
    private:
        string webPort;
        string worldPort;
        string worldHost;
        string upsPort;
        size_t worldID;
        int worldFD;
        int upsFD;

        int whNum;
        vector<Warehouse> whs;
        
        //handle gpb msg
        unique_ptr<gpbIn> worldReader;
        unique_ptr<gpbOut> worldWriter;
        unique_ptr<gpbIn> upsReader;
        unique_ptr<gpbOut> upsWriter;
        //init 
        void initializeWorldCommunication();
        void initializeUpsCommunication();
        
        //connect world
        void connectWorld();
        void initAconnect(AConnect & aconnect);
        void AWHandshake(AConnect & aconnect, AConnected & aconnected);

        //connect ups
        void connectUps();
        void initAUConnectCommand(AUCommands & aucommand);
        
        //run
        void processReceivedWorldMessages();
        void processReceivedUpsMessages();
        void sendMessagesToWorld();
        void sendMessagesToUps();
        void printAMessage(const ACommands & msg);
        void printAUMessage(const AUCommands & msg);
        void processOrderFromWeb(const int serverFD);

        Server();
        Server(Server &) = delete;
        Server & operator=(const Server &) = delete;

    public:  
        vector<bool> seqNumTable;  
        int seqNum;          
        mutex seqNum_lock;          

        unordered_set<int> worldAckedSet;
        unordered_set<int> upsAckedSet;

        MsgQueue<ACommands> worldQueue;
        MsgQueue<AUCommands> upsQueue;

        queue<int> orderQueue;
        mutex order_lck;

        
        static Server & getInstance();
        static connection * connectDB(string dbName, string userName, string password);
        static void disConnectDB(connection * C);
        void run();
        size_t requireSeqNum(); 
        vector<Warehouse> getWhs() { return whs; }
        int getWorldID(){return worldID;}
};

#endif