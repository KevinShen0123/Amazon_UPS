#include "bufferProcessing.hpp" 
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
UInitTruck uInitTruck(google::protobuf::int32 id,google::protobuf::int32 x,google::protobuf::int32 y){
    UInitTruck uit;
    uit.set_id(id);
    uit.set_x(x);
    uit.set_y(y);
    return uit;
}
UConnect uConnect(bool useWID,int wID, std::vector<UInitTruck> ts, bool isAmazon){
UConnect uc;
uc.set_isamazon(isAmazon);
if(useWID){
    uc.set_worldid(wID);
}
for(int i=0;i<ts.size();i++){
    UInitTruck* t1=uc.add_trucks();
    t1->set_id(ts[i].id());
    t1->set_x(ts[i].x());
    t1->set_y(ts[i].y());
}
return uc;
}
UConnected uConnected(google::protobuf::int32 worldid, google::protobuf::string result){
    UConnected ucd;
    ucd.set_result(result);
    ucd.set_worldid(worldid);
    return ucd;
}
UGoPickup uGoPickUP(google::protobuf::int32 truckid,google::protobuf::int32 whid,google::protobuf::int64 seqnum){
UGoPickup ugp;
ugp.set_seqnum(seqnum);
ugp.set_truckid(truckid);
ugp.set_whid(whid);
return ugp;
}
UFinished uFinished(google::protobuf::int32 truck_id, google::protobuf::int32 x , google::protobuf::int32 y, google::protobuf::string status,google::protobuf::int64 seqnum ){
    UFinished ufd;
    ufd.set_seqnum(seqnum);
    ufd.set_status(status);
    ufd.set_truckid(truck_id);
    ufd.set_x(x);
    ufd.set_y(y);
    return ufd;
}
UDeliveryMade uDeliveryMade(google::protobuf::int32 truck_id ,google::protobuf::int64 package_id,google::protobuf::int64 seq_num){
    UDeliveryMade UDM;
    UDM.set_seqnum(seq_num);
    UDM.set_truckid(truck_id);
    UDM.set_packageid(package_id);
    return UDM;
}
UDeliveryLocation uDeliveryLocation(google::protobuf::int64 package_id,google::protobuf::int32 x,google::protobuf::int32 y){
    UDeliveryLocation udl;
    udl.set_packageid(package_id);
    udl.set_x(x);
    udl.set_y(y);
    return udl;
}
UGoDeliver uGoDeliver(google::protobuf::int32 truck_id,google::protobuf::int64 seqnum,std::vector<UDeliveryLocation> locations){
    UGoDeliver UGD;
    UGD.set_seqnum(seqnum);
    UGD.set_truckid(truck_id);
    for(int i=0;i<locations.size();i++){
       UDeliveryLocation* UGD1= UGD.add_packages();
       UGD1->set_packageid(locations[i].packageid());
       UGD1->set_x(locations[i].x());
       UGD1->set_y(locations[i].y());
    }
    return UGD;
}
UErr uErr(google::protobuf::string error, google::protobuf::int64 originalseqnum,google::protobuf::int64 seqnum){
    UErr uerr;
    uerr.set_err(error);
    uerr.set_originseqnum(originalseqnum);
    uerr.set_seqnum(seqnum);
    return uerr;
}
UQuery uqery(google::protobuf::int32 truck_id,google::protobuf::int64 seqnum){
    UQuery query;
    query.set_seqnum(seqnum);
    query.set_truckid(truck_id);
    return query;
}
UTruck uTruck(google::protobuf::int32 truck_id, google::protobuf::string status,google::protobuf::int32 x,google::protobuf::int32 y,google::protobuf::int64 seqnum){
UTruck truck;
truck.set_seqnum(seqnum);
truck.set_x(x);
truck.set_y(y);
truck.set_status(status);
truck.set_truckid(truck_id);
return truck;
}
UCommands uCommands(std::vector<UGoPickup> ugps,std::vector<UGoDeliver> ugds,bool has_sim_speed, google::protobuf::int32 simspeed, bool has_disconnect, bool disconnect,std::vector<UQuery> querys,std::vector<google::protobuf::int64> acks){
UCommands ucs;
for(int i=0;i<ugps.size();i++){
    UGoPickup* ugp=ucs.add_pickups();
    ugp->set_seqnum(ugps[i].seqnum());
    ugp->set_truckid(ugps[i].truckid());
    ugp->set_whid(ugps[i].whid());
}
for(int j=0;j<ugds.size();j++){
UGoDeliver* ugd=ucs.add_deliveries();
ugd->set_seqnum(ugds[j].seqnum());
ugd->set_truckid(ugds[j].truckid());
for(int k=0;k<ugds[j].packages().size();k++){
   UDeliveryLocation* udlk=ugd->add_packages();
   udlk->set_packageid(ugds[j].packages().Get(k).packageid());
   udlk->set_x(ugds[j].packages().Get(k).x());
   udlk->set_y(ugds[j].packages().Get(k).y());
 }
}
if(has_sim_speed){
    ucs.set_simspeed(simspeed);
}
if(has_disconnect){
    ucs.set_disconnect(disconnect);
}
for(int m=0;m<querys.size();m++){
    UQuery* uq=ucs.add_queries();
    uq->set_seqnum(querys[m].seqnum());
    uq->set_truckid(querys[m].truckid());
}
for(int p=0;p<acks.size();p++){
  ucs.add_acks(acks[p]);
}
return ucs;
}
UResponses uResponses(std::vector<UFinished> ufs, std::vector<UDeliveryMade> udms, bool has_finished, bool finished,std::vector<google::protobuf::int64> acks,std::vector<UTruck> trucks,std::vector<UErr> errors){
UResponses urs;
for(int i=0;i<acks.size();i++){
    urs.add_acks(acks[i]);
}
for(int j=0;j<ufs.size();j++){
    UFinished*uf=urs.add_completions();
    uf->set_seqnum(ufs[j].seqnum());
    uf->set_status(ufs[j].status());
    uf->set_truckid(ufs[j].truckid());
    uf->set_x(ufs[j].x());
    uf->set_y(ufs[j].y());
}
for(int k=0;k<udms.size();k++){
    UDeliveryMade* udm=urs.add_delivered();
    udm->set_packageid(udms[k].packageid());
    udm->set_seqnum(udms[k].seqnum());
    udm->set_truckid(udms[k].truckid());
}
if(has_finished){
    urs.set_finished(finished);
}
for(int p=0;p<trucks.size();p++){
    UTruck* uts=urs.add_truckstatus();
    uts->set_seqnum(trucks[p].seqnum());
    uts->set_status(trucks[p].status());
    uts->set_truckid(trucks[p].truckid());
    uts->set_x(trucks[p].x());
    uts->set_y(trucks[p].y());
}
for(int q=0;q<errors.size();q++){
 UErr* e1=urs.add_error();
 e1->set_originseqnum(errors[q].originseqnum());
 e1->set_seqnum(errors[q].seqnum());
}
return urs;
}
std::string UCommands_toString(UCommands uc){
    return uc.SerializeAsString();
}
UCommands string_to_UCommands(std::string UC){
    UCommands uc;
    bool isUC=uc.ParseFromString(UC);
    if(isUC==false){
        throw std::exception();
    }
    return uc;
}
UResponses string_to_UResponses(std::string urs){
   UResponses urs2;
    bool isURS=urs2.ParseFromString(urs);
    if(isURS==false){
        throw std::exception();
    }
    return urs2;
}