from google.protobuf.internal.decoder import _DecodeVarint32
import world_ups_pb2
from google.protobuf.internal.encoder import _EncodeVarint
import amazon_ups_pb2
def to_UGoPickUp(truck_id,whid,seqnum):
    UGP=world_ups_pb2.UGoPickup()
    UGP.truckid=truck_id
    UGP.whid=whid
    UGP.seqnum=seqnum
    return UGP
def to_UDeliverLOcation(package_id,x,y):
    UDL=world_ups_pb2.UDeliveryLocation()
    UDL.packageid=package_id
    UDL.x=x
    UDL.y=y
    return UDL
def to_UGoDeliver(truck_id,UDeliverLocations,seqnum):
    UGDL=world_ups_pb2.UGoDeliver()
    UGDL.truckid=truck_id
    UGDL.seqnum=seqnum
    for location in UDeliverLocations:
        UGDL.packages.append(location)
    return UGDL
def to_UQuery(truckid,seqnum):
    UQuery=world_ups_pb2.UQuery()
    UQuery.truckid=truckid
    UQuery.seqnum=seqnum
    return UQuery
def to_UInitTruck(id,x,y):
    uInitTruck=world_ups_pb2.UInitTruck()
    uInitTruck.id=id
    uInitTruck.x=x
    uInitTruck.y=y
    return uInitTruck
def to_uCommands(pickups,delivers,hassimspeed,simspeed,hasdisconnect,disconnect,querys,acks):
    uCommands=world_ups_pb2.UCommands()
    for pickup in pickups:
        uCommands.pickups.append(pickup)
    for deliver in delivers:
        uCommands.deliveries.append(deliver)
    if hassimspeed:
        uCommands.simspeed=simspeed
    if hasdisconnect:
        uCommands.disconnect=disconnect
    for query in querys:
         uCommands.queries.append(query)
    for ack in acks:
        uCommands.acks.append(ack)
def to_UAConnectedToWorld(worldid,seqnum):
    uAConnectedToWorld=amazon_ups_pb2.UAConnectedToWorld()
    uAConnectedToWorld.worldid=worldid
    uAConnectedToWorld.seqnum=seqnum
    return uAConnectedToWorld
def to_UADestinationUpdated(order_id,destx,desty,seqnum):
      uADestinationUpdated=amazon_ups_pb2.UADestinationUpdated()
      uADestinationUpdated.orderid=order_id
      uADestinationUpdated.destinationx=destx
      uADestinationUpdated.destinationy=desty
      uADestinationUpdated.seqnum=seqnum
      return uADestinationUpdated
def to_UATruckArrived(truckid,whnum,seqnum):
    uATruckArrived=amazon_ups_pb2.UATruckArrived()
    uATruckArrived.truckid=truckid
    uATruckArrived.whnum=whnum
    uATruckArrived.seqnum=seqnum
    return uATruckArrived
def to_UAOrderDeparture(orderid,packageid,trackingnum,seqnum):
    uAOrderDeparture=amazon_ups_pb2.UAOrderDeparture()
    uAOrderDeparture.orderid=orderid
    uAOrderDeparture.packageid=packageid
    uAOrderDeparture.trackingnum=trackingnum
    uAOrderDeparture.seqnum=seqnum
    return uAOrderDeparture
def to_UAOrderDelivered(packageid,destx,desty,seqnum):
    uAOrderDelivered=amazon_ups_pb2.UAOrderDelivered()
    uAOrderDelivered.packageid=packageid
    uAOrderDelivered.destinationx=destx
    uAOrderDelivered.destinationy=desty
    uAOrderDelivered.seqnum=seqnum
    return uAOrderDelivered
def to_UACommands(connectedtoworlds,destinationupdateds,truckarrives,orderdepartures,orderdelivers,acks,errors):
    uACommands=amazon_ups_pb2.UACommands()
    for connectedtoworlda in connectedtoworlds:
        uACommands.connectedtoworld.append(connectedtoworlda)
    for destinationupdate in destinationupdateds:
        uACommands.destinationupdated.append(destinationupdate)
    for truckarrive in truckarrives:
        uACommands.trcukarrived.append(truckarrive)
    for orderdepartureone in orderdepartures:
        uACommands.orderdeparture.append(orderdepartureone)
    for orderdeliverone in orderdelivers:
        uACommands.orderdelivered.append(orderdeliverone)
    for ack in acks:
        uACommands.acks.append(ack)
    for err in errors:
        uACommands.error.append(err)
    return uACommands
def toErr(err,originalseqnum,seqnum):
    err1=amazon_ups_pb2.Err()
    err1.err=err
    err1.originalseqnum=originalseqnum
    err1.seqnum=seqnum
    return err1