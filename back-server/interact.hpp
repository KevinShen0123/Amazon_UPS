#include  "querys.hpp"
#include "socketutil.hpp"
#include "bufferProcessing.hpp"
#include "world_ups.pb.h"

int connectToDatabase();

int connectToWorld(const char * hostname, const char * port, int worldId);

int connectToAmazon(const char * hostname, const char * port);

int connectToFrontend(const char * hostname, const char * port);

int handleWorldConnection();

int handleAmazonConnection();




