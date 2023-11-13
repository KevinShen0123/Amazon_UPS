#include "sqlOperation.h"

void insertSampleData(connection* C) {
    try {
        work W(*C);

        // Insert data into USER_PROFILE
        W.exec("INSERT INTO USER_PROFILE (USER_NAME, ADDRX, ADDRY, UPSID) VALUES (1, '123', '456', 'UPS001'), (2, '789', '101', 'UPS002');");
        // Insert data into PRODUCT
        W.exec("INSERT INTO PRODUCT (PRODUCT_ID, PRODUCT_NAME, PRODUCT_DESC, PRICE, CATALOG) VALUES (1, 'Product A', 'Description A', 19.99, 'Electronics'), (2, 'Product B', 'Description B', 29.99, 'Home Appliances');");

        // Insert data into ORDER
        W.exec("INSERT INTO \"ORDER\" (ORDER_ADDR_X, ORDER_ADDR_Y, TIME, ORDER_OWNER_ID, UPS_ID, PRICE) VALUES (111, 222, '12:34:56', 1, 1001, 49.99);");
        W.exec("INSERT INTO \"ORDER\" (ORDER_ADDR_X, ORDER_ADDR_Y, TIME, ORDER_OWNER_ID, UPS_ID, PRICE) VALUES (333, 444, '22:34:56', 2, 1002, 99.99);");
        // Insert data into PACKAGE
        W.exec("INSERT INTO PACKAGE (PACKAGE_DESC, PACKAGE_OWNER_ID, AMOUNT, PRODUCT_ID, WH_ID, ORDER_ID, STATUS) VALUES ('Sample Package 1', 1, 3, 1, 1, 1, 'packing');");
        

        W.commit();
    } catch (const exception &e) {
        cerr << e.what() << endl;
        return;
    }
}
/*
    read sql command from the file and then create tabel using connection *C.
    If fails, it will throw exception.
*/
void createTable(connection * C, string fileName) {
  cout << "Starting create new Tables..." << endl;
  string sql;
  ifstream ifs(fileName.c_str(), ifstream::in);
  if (ifs.is_open() == true) {
    string line;
    while (getline(ifs, line))
      sql.append(line);
  }
  else {
    throw MyException("fail to open file.");
  }

  work W(*C);
  W.exec(sql);
  W.commit();
  cout << "Finishing create new Tables..." << endl;
}

/*
    Drop all the table in the DataBase. Using for test.
*/
void dropAllTable(connection *C) {
  cout << "Starting Drop all the existed table..." << endl;
  work W(*C);

  W.exec("DROP TABLE IF EXISTS PACKAGE;");
  W.exec("DROP TABLE IF EXISTS \"ORDER\";");
  W.exec("DROP TABLE IF EXISTS PRODUCT;");
  W.exec("DROP TABLE IF EXISTS USER_PROFILE;");

  W.commit();
  cout << "Finishing Drop all the existed table..." << endl;
}



//when reveive a order_id from the web-page, it will query the packages included in the order
std::vector<std::string> getPackagesfOrder(connection * C, int order_id)
{
    nontransaction N(*C);
    stringstream sql;


    sql << "SELECT PACKAGE_ID FROM PACKAGE WHERE "
         "ORDER_ID_ID= " << order_id << ";";


    // execute sql statement and get the result set
    result package_result(N.exec(sql.str()));
   

    // Convert the result set to a list of strings
    std::vector<std::string> packages;
    for (auto row = package_result.begin(); row != package_result.end(); ++row) {
        for (auto col = row->begin(); col != row->end(); ++col) {
            packages.push_back(col->as<std::string>());
        }
    }       

    return packages;

    
}


//one package means one purchase action,it will change the status of the package to packing and set its wh_id
//you can use updatepackWhID and updatepackPacking to complete this fucntion individually
void purchaseProduct(connection * C, int package_id,int wh_id)
{
    work W(*C);
    stringstream sql;
    sql << "UPDATE PACKAGE SET STATUS= " << W.quote("packing") << ", WH_ID= " 
        << wh_id << " WHERE PACKAGE_ID= "<< package_id << ";";
    W.exec(sql.str());
    W.commit();
}

int getOrderAddrx(connection* C, int order_id)
{
    try
    {
        nontransaction N(*C);
        stringstream sql;
        sql << "SELECT ORDER_ADDR_X FROM \"ORDER\" WHERE "
            "ORDER_ID= " << order_id << ";";
        // execute sql statement and get the result set
        result order_x_result(N.exec(sql.str()));

        // Check if there's a result
        if (order_x_result.empty())
        {
            std::cerr << "No result found for ORDER_ID: " << order_id << std::endl;
            return -1;
        }

        // Then we need to get the order address x from result
        int order_x = order_x_result[0][0].as<int>();

        // Close the nontransaction object
        N.commit();

        return order_x;
    }
    catch (const std::exception &e)
    {
        std::cerr << "Error: " << e.what() << std::endl;
        return -1;
    }
}

int getOrderAddry(connection* C, int order_id)
{

    nontransaction N(*C);
    stringstream sql;


    sql << "SELECT ORDER_ADDR_Y FROM \"ORDER\" WHERE "
        "ORDER_ID= " << order_id << ";";


    // execute sql statement and get the result set
    result order_y_result(N.exec(sql.str()));


    // Then we need to get inventory item amount from result R
    int order_y = order_y_result[0][0].as<int>();
    return order_y;


}

string getOrderUPSID(connection* C, int order_id)
{

    nontransaction N(*C);
    stringstream sql;


    sql << "SELECT UPSID FROM \"ORDER\" WHERE "
        "ORDER_ID= " << order_id << ";";


    result ups_id_result(N.exec(sql.str()));
    string ups_id = ups_id_result[0][0].as<string>();

    return ups_id;


}

vector<int> getPackageIDs(connection* C, int order_id) {
    vector<int> package_ids;
    nontransaction N(*C);

    stringstream sql;
    sql << "SELECT PACKAGE_ID FROM PACKAGE WHERE ORDER_ID = " << order_id << ";";

    result R(N.exec(sql.str()));

    for (auto row : R) {
        int package_id;
        row[0].to(package_id);
        package_ids.push_back(package_id);
    }

    return package_ids;
}


int getPackageProductID(connection* C, int package_id)
{
    nontransaction N(*C);
    stringstream sql;


    sql << "SELECT PRODUCT_ID FROM PACKAGE WHERE "
        "PACKAGE_ID= " << package_id << ";";


    // execute sql statement and get the result set
    result product_id_result(N.exec(sql.str()));


    // Then we need to get inventory item amount from result R
    int product_id = product_id_result[0][0].as<int>();

    return product_id;


    


}



string getPackageProductDesc(connection* C, int package_id)
{
    nontransaction N(*C);
    stringstream sql,sql_new;


    sql << "SELECT PRODUCT_ID FROM PACKAGE WHERE "
        "PACKAGE_ID= " << package_id << ";";

    // execute sql statement and get the result set
    result product_id_result(N.exec(sql.str()));

    // Then we need to get inventory item amount from result R
    int product_id = product_id_result[0][0].as<int>();

    sql_new << "SELECT PRODUCT_DESC FROM PRODUCT WHERE "
        "PRODUCT_ID= " << product_id << ";";

    // execute sql statement and get the result set
    result product_desc_result(N.exec(sql_new.str()));
    string product_desc = product_desc_result[0][0].as<string>();

    return product_desc;


}


int getPackageOrderID(connection* C, int package_id) {
    nontransaction N(*C);

    stringstream sql;
    sql << "SELECT ORDER_ID FROM PACKAGE WHERE PACKAGE_ID = " << package_id << ";";

    result R(N.exec(sql.str()));

    int order_id = -1;
    if (!R.empty()) {
        R[0][0].to(order_id);
    }

    return order_id;
}


int getPackageUpsID(connection* C, int package_id) {
    nontransaction N(*C);

    stringstream sql;
    sql << "SELECT O.UPSID FROM PACKAGE P "
           "JOIN \"ORDER\" O ON P.ORDER_ID = O.ORDER_ID "
           "WHERE P.PACKAGE_ID = " << package_id << ";";

    result R(N.exec(sql.str()));

    int ups_id = -1;
    if (!R.empty()) {
        R[0][0].to(ups_id);
    }

    return ups_id;
}


string getPackageDesc(connection* C, int package_id)
{
    nontransaction N(*C);
    stringstream sql;


    sql << "SELECT PACKAGE_DESC FROM PACKAGE WHERE "
        "PACKAGE_ID= " << package_id << ";";


    // execute sql statement and get the result set
    result package_desc_result(N.exec(sql.str()));


    // Then we need to get inventory item amount from result R
    string package_desc = package_desc_result[0][0].as<string>();
    return package_desc;



}




int getPackageAmount(connection* C, int package_id)
{
    nontransaction N(*C);
    stringstream sql;


    sql << "SELECT AMOUNT FROM PACKAGE WHERE "
        "PACKAGE_ID= " << package_id << ";";


    // execute sql statement and get the result set
    result package_amount_result(N.exec(sql.str()));


    // Then we need to get inventory item amount from result R
    int package_amount = package_amount_result[0][0].as<int>();
    return package_amount;



}

void updateOrderAddr(connection* C, int orderID, int new_x, int new_y) {
    work W(*C);
    stringstream sql;
    sql << "UPDATE \"ORDER\" SET ORDER_ADDR_X = " << new_x
        << ", ORDER_ADDR_Y = " << new_y
        << " WHERE ORDER_ID = " << orderID << ";";

    W.exec(sql.str());
    W.commit();
} 
vector<int> getPackedPackageIDs(connection* C, int wh_id) {
    vector<int> package_ids;
    nontransaction N(*C);

    stringstream sql;
    sql << "SELECT PACKAGE_ID FROM PACKAGE WHERE STATUS = 'packed' AND WH_ID = " << wh_id << ";";

    result R(N.exec(sql.str()));

    for (auto row : R) {
        int package_id;
        row[0].to(package_id);
        package_ids.push_back(package_id);
    }

    return package_ids;
}

void setPackagesWhID(connection* C, int orderID, int whID)
{

    work W(*C);
    stringstream sql;
    sql << "UPDATE PACKAGE SET WH_ID= " << whID
        << " WHERE ORDER_ID= " << orderID << ";";

    W.exec(sql.str());
    W.commit();

}

void setOrderUpsID(connection *C, int wh_id, int ups_id) {
    work W(*C);
    stringstream sql;
    sql << "UPDATE \"ORDER\" SET UPSID = " << ups_id
        << " WHERE ORDER_ID IN (SELECT ORDER_ID FROM PACKAGE WHERE WH_ID = " << wh_id << ");";

    W.exec(sql.str());
    W.commit();
}

void updatepackPacking(connection* C, int package_id)
{

    work W(*C);
    stringstream sql;


    sql << "UPDATE PACKAGE SET STATUS =  'packing' "
        << " WHERE PACKAGE_ID= " << package_id << ";";

    W.exec(sql.str());
    W.commit();

}


//update the status of package into packed
void updatepackPacked(connection * C, int package_id)
{

    work W(*C);
    stringstream sql;


    sql << "UPDATE PACKAGE SET STATUS=  'packed'" 
         << " WHERE PACKAGE_ID= "<< package_id << ";";

    W.exec(sql.str());
    W.commit();

}

//update the status of package into packed
void updatepackLoading(connection * C, int package_id)
{

    work W(*C);
    stringstream sql;


    sql << "UPDATE PACKAGE SET STATUS= 'loading'" 
         << " WHERE PACKAGE_ID= "<< package_id << ";";

    W.exec(sql.str());
    W.commit();

}

//update the status of package into packed
void updatepackLoaded(connection * C, int package_id)
{

    work W(*C);
    stringstream sql;


    sql << "UPDATE PACKAGE SET STATUS= 'loaded' "
         << " WHERE PACKAGE_ID= "<< package_id << ";";

    W.exec(sql.str());
    W.commit();

}

//update the status of package into packed
void updatepackDelivering(connection * C, int package_id)
{

    work W(*C);
    stringstream sql;


    sql << "UPDATE PACKAGE SET STATUS= 'delivering' " 
         << " WHERE PACKAGE_ID= "<< package_id << ";";

    W.exec(sql.str());
    W.commit();

}

//update the status of package into packed
void updatepackDelivered(connection * C, int package_id)
{

    work W(*C);
    stringstream sql;


    sql << "UPDATE PACKAGE SET STATUS= 'delivered' " 
         << " WHERE PACKAGE_ID= "<< package_id << ";";

    W.exec(sql.str());
    W.commit();

}



