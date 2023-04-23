//or database querys, update the database
#include "querys.hpp"


void addTruck(connection *C, int x, int y, string status){
		work W(*C);

    string sql_base = "INSERT INTO TRUCK (X, Y, STATUS) VALUES (";
    stringstream ss; 
    ss<<sql_base<<x<<","<<y<<","<<W.quote(status)<<");";
		string sql = ss.str();
    
    W.exec(sql);
    W.commit();
}

void addDelivery(connection *C, int orderId, int packageId, int dest_x, int dest_y, int truckId, string status){
		work W(*C);

		string sql_base = "INSERT INTO DELIVERY (ORDER_ID, PACKAGE_ID, DEST_X, DEST_Y, TRUCK_ID, STATUS) VALUES (";
    stringstream ss; 
    ss<<sql_base<<orderId<<","<<packageId<<","<<dest_x<<","<<dest_y<<","<<truckId<<","<<W.quote(status)<<");";
		string sql = ss.str();
    
    W.exec(sql);
    W.commit();

}

void addOrder(connection *C, int orderId, string upsaccout, int dest_x, int dest_y){
		work W(*C);

		string sql_base = "INSERT INTO ORDER (ORDER_ID, UPSACCOUNT, DEST_X, DEST_Y) VALUES (";
    stringstream ss; 
    ss<<sql_base<<orderId<<","<<W.quote(upsaccout)<<","<<dest_x<<","<<dest_y<<");";
		string sql = ss.str();
    
    W.exec(sql);
    W.commit();
}


void updateTruckStatus(connection *C, int truckId, string status){
		work W(*C);

		string sql_base = "UPDATE TRUCK SET STATUS = ";
    stringstream ss; 
    ss<<sql_base<<W.quote(status)<<" WHERE TRUCK_ID = "<<truckId<<";";
		string sql = ss.str();
    
    W.exec(sql);
    W.commit();
}

void updateDeliveryStatus(connection *C, int packageId, string status){
		work W(*C);

		string sql_base = "UPDATE DELIVERY SET STATUS = ";
    stringstream ss; 
    ss<<sql_base<<W.quote(status)<<" WHERE PACKAGE_ID = "<<packageId<<";";
		string sql = ss.str();
    
    W.exec(sql);
    W.commit();
}

void updateDeliveryAddress(connection *C, int packageId, int dest_x, int dest_y){
		work W(*C);

		string sql_base = "UPDATE DELIVERY SET DEST_X = ";
    stringstream ss; 
    ss<<sql_base<<dest_x<<", DEST_Y = "<<dest_y<<" WHERE PACKAGE_ID = "<<packageId<<";";
		string sql = ss.str();
    
    W.exec(sql);
    W.commit();
}

void getTruckDelivery(connection *C, int truckId){
	
}

void getTruckStatus(connection *C, int truckid){

}