#include <unistd.h>
#include <iostream>
#include <google/protobuf/message.h>
#include <google/protobuf/descriptor.h>
#include <google/protobuf/io/zero_copy_stream_impl.h>
#include <google/protobuf/io/coded_stream.h>
#include <google/protobuf/io/zero_copy_stream_impl_lite.h>
#include  "amazon_ups.pb.h"
#include "world_ups.pb.h"
#include <cstdbool>
using namespace google::protobuf::io;
UInitTruck uInitTruck(google::protobuf::int32 id,google::protobuf::int32 x,google::protobuf::int32 y);
UConnect uConnect(bool useWID,int wID, std::vector<UInitTruck> ts, bool isAmazon);
UAConnectedToWorld uAConnectedToWorld(google::protobuf::int64 world_id,google::protobuf::int64 seq_num);
UADestinationUpdated uADestinationUpdated(google::protobuf::int32 order_id,google::protobuf::int32 destinationx,google::protobuf::int32 destinationy,google::protobuf::int64 seqnum);
UATruckArrived uATruckArrived(google::protobuf::int32 truckid,google::protobuf::int32 whnum,google::protobuf::int64 seqnum);
UAOrderDeparture uAOrderDeparture(google::protobuf::int32 order_id,google::protobuf::int64 packageid,google::protobuf::int64 trackingnum,google::protobuf::int64 seqnum);
UAOrderDelivered uAOrderDelivered(google::protobuf::int64 packageid,google::protobuf::int32 destinationx, google::protobuf::int32 destinationy,google::protobuf::int64 seqnum);
Err err(std::string error,google::protobuf::int64 originalseqnum,google::protobuf::int64 seqnum);
UACommands uACommands(std::vector<UAConnectedToWorld> uacts,std::vector<UADestinationUpdated> uadu,std::vector<UATruckArrived> uatu,std::vector<UAOrderDeparture> uadou,std::vector<UAOrderDelivered> uaod,std::vector<google::protobuf::int64> acks,std::vector<Err> errors);

UConnected uConnected(google::protobuf::int32 worldid, google::protobuf::string result);
UGoPickup uGoPickUP(google::protobuf::int32 truckid,google::protobuf::int32 whid,google::protobuf::int64 seqnum);
UFinished uFinished(google::protobuf::int32 truck_id, google::protobuf::int32 x , google::protobuf::int32 y, google::protobuf::string status,google::protobuf::int64 seqnum );
UDeliveryMade uDeliveryMade(google::protobuf::int32 truck_id ,google::protobuf::int64 package_id,google::protobuf::int64 seq_num);
UDeliveryLocation uDeliveryLocation(google::protobuf::int64 package_id,google::protobuf::int32 x,google::protobuf::int32 y);
UGoDeliver uGoDeliver(google::protobuf::int32 truck_id,google::protobuf::int64 seqnum,std::vector<UDeliveryLocation> locations);
UErr uErr(google::protobuf::string error, google::protobuf::int64 originalseqnum,google::protobuf::int64 seqnum);
UQuery uqery(google::protobuf::int32 truck_id,google::protobuf::int64 seqnum);
UTruck uTruck(google::protobuf::int32 truck_id, google::protobuf::string status,google::protobuf::int32 x,google::protobuf::int32 y,google::protobuf::int64 seqnum);
UCommands uCommands(std::vector<UGoPickup> ugps,std::vector<UGoDeliver> ugds,bool has_sim_speed, google::protobuf::int32 simspeed, bool has_disconnect, bool disconnect,std::vector<UQuery> querys,std::vector<google::protobuf::int64> acks);
UResponses uResponses(std::vector<UFinished> ufs, std::vector<UDeliveryMade> udms, bool has_finished, bool finished,std::vector<google::protobuf::int64> acks,std::vector<UTruck> trucks,std::vector<UErr> errors);
std::string UCommands_toString(UCommands uc);
std::string UResponses_to_string(UResponses urs);
UCommands string_to_UCommands(std::string UC);
UResponses string_to_UResponses(std::string urs);
UACommands string_to_UACommands(std::string UAC);
std::string UACommands_to_string(UACommands uac);
AUCommands string_to_AUCommands(std::string auc);




