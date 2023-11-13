#ifndef _WAREHOUSE_H
#define _WAREHOUSE_H

#include <iostream>
using namespace std;

class Warehouse {
 private:
  int x;
  int y;
  int id;

 public:
  Warehouse(int x, int y, int id) : x(x), y(y), id(id) {}
  ~Warehouse() {}
  int getX() const { return x; }
  int getY() const { return y; }
  int getID() const { return id; }
};

#endif