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
UAConnectedToWorld uAConnectedToWorld(google::protobuf::int64 world_id,google::protobuf::int64 seq_num){
    UAConnectedToWorld uac;
    uac.set_seqnum(seq_num);
    uac.set_worldid(world_id);
    return uac;
}
UADestinationUpdated uADestinationUpdated(google::protobuf::int32 order_id,google::protobuf::int32 destinationx,google::protobuf::int32 destinationy,google::protobuf::int64 seqnum){
    UADestinationUpdated udu;
    udu.set_destinationx(destinationx);
    udu.set_destinationy(destinationy);
    udu.set_seqnum(seqnum);
    udu.set_orderid(order_id);
    return udu;
}
UATruckArrived uATruckArrived(google::protobuf::int32 truckid,google::protobuf::int32 whnum,google::protobuf::int64 seqnum){
   UATruckArrived uat;
   uat.set_seqnum(seqnum);
   uat.set_truckid(truckid);
   uat.set_whnum(whnum);
   return uat;
}
UAOrderDeparture uAOrderDeparture(google::protobuf::int32 order_id,google::protobuf::int64 packageid,google::protobuf::int64 trackingnum,google::protobuf::int64 seqnum){
 UAOrderDeparture uaod;
 uaod.set_orderid(order_id);
 uaod.set_packageid(packageid);
 uaod.set_seqnum(seqnum);
 uaod.set_trackingnum(trackingnum);
 return uaod;
}
UAOrderDelivered uAOrderDelivered(google::protobuf::int64 packageid,google::protobuf::int32 destinationx, google::protobuf::int32 destinationy,google::protobuf::int64 seqnum){
  UAOrderDelivered uaodd;
  uaodd.set_destinationx(destinationx);
  uaodd.set_destinationy(destinationy);
  uaodd.set_seqnum(seqnum);
  uaodd.set_packageid(packageid);
  return uaodd;
}
Err err(std::string error,google::protobuf::int64 originalseqnum,google::protobuf::int64 seqnum){
    Err err1;
    err1.set_err(error);
    err1.set_originseqnum(originalseqnum);
    err1.set_seqnum(seqnum);
    return err1;
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
UACommands uACommands(std::vector<UAConnectedToWorld> uacts,std::vector<UADestinationUpdated> uadu,std::vector<UATruckArrived> uatu,std::vector<UAOrderDeparture> uadou,std::vector<UAOrderDelivered> uaod,std::vector<google::protobuf::int64> acks,std::vector<Err> errors){
UACommands ua;
for(int a=0;a<uacts.size();a++){
    UAConnectedToWorld* uact1=ua.add_connectedtoworld();
    uact1->set_seqnum(uacts[a].seqnum());
    uact1->set_worldid(uacts[a].worldid());
}
for(int b=0;b<uadu.size();b++){
    UADestinationUpdated*uadu1=ua.add_destinationupdated();
    uadu1->set_destinationx(uadu[b].destinationx());
    uadu1->set_destinationy(uadu[b].destinationy());
    uadu1->set_orderid(uadu[b].orderid());
    uadu1->set_seqnum(uadu[b].seqnum());
}
for(int c=0;c<uatu.size();c++){
    UATruckArrived* uatu1=ua.add_truckarrived();
    uatu1->set_seqnum(uatu[c].seqnum());
    uatu1->set_truckid(uatu[c].truckid());
    uatu1->set_whnum(uatu1[c].whnum());
}
for(int d=0;d<uaod.size();d++){
    UAOrderDelivered*uadou1=ua.add_orderdelivered();
    uadou1->set_destinationx(uaod[d].destinationx());
    uadou1->set_destinationy(uaod[d].destinationy());
    uadou1->set_packageid(uaod[d].packageid());
    uadou1->set_seqnum(uaod[d].seqnum());
}
for(int e=0;e<uadou.size();e++){
    UAOrderDeparture*uadou2=ua.add_orderdeparture();
   uadou2->set_orderid(uadou[e].orderid());
   uadou2->set_packageid(uadou[e].packageid());
   uadou2->set_seqnum(uadou[e].seqnum());
   uadou2->set_trackingnum(uadou[e].trackingnum());
}
for(int f=0;f<acks.size();f++){
    ua.add_acks(acks[f]);
}
for(int g=0;g<errors.size();g++){
   Err* e1= ua.add_error();
   e1->set_err(errors[g].err());
   e1->set_originseqnum(errors[g].originseqnum());
   e1->set_seqnum(errors[g].seqnum());
}
return ua;
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
std::string UResponses_to_string(UResponses urs){
   return urs.SerializeAsString();
}
UResponses string_to_UResponses(std::string urs){
   UResponses urs2;
    bool isURS=urs2.ParseFromString(urs);
    if(isURS==false){
        throw std::exception();
    }
    return urs2;
}
UACommands string_to_UACommands(std::string UAC){
   UACommands uc;
    bool isUAC=uc.ParseFromString(UAC);
    if(isUAC==false){
        throw std::exception();
    }
    return uc;
}
std::string UACommands_to_string(UACommands uac){
    return uac.SerializeAsString();
}
AUCommands string_to_AUCommands(std::string auc){
    AUCommands AUC;
    bool isAUC=AUC.ParseFromString(auc);
    if(isAUC==false){
        throw std::exception();
    }
    return AUC;
}
