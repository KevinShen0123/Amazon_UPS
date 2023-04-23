#include <cstdlib>
#include <stdlib.h>
#include <stdio.h>
#include <fstream>
#include <ostream>
#include <sstream>
#include <iostream>
#include <string>

using namespace std;

class Truck {
    public:
        int truckId;
        int x;
        int y;
};

class Delivery {
    public:
        int id;
        int orderId;
        int packageId;
        int dest_x;
        int dest_y;
        int truckId;
        string status;
};