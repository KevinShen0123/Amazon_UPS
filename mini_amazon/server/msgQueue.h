#ifndef _MSGQUEUE_H
#define _MSGQUEUE_H

#include <condition_variable>
#include <memory>
#include <mutex>
#include <queue>

using namespace std;

template<typename T>
class MsgQueue {
 private:
  queue<T> data_queue;
  mutex mtx;
  condition_variable cv;

 public:
  MsgQueue() {}

  MsgQueue(MsgQueue const & other) {
    lock_guard<mutex> lock(other.mtx);
    data_queue = other.data_queue;
  }

  void push(const T & newValue) {
    lock_guard<mutex> lock(mtx);
    data_queue.push(newValue);
    cv.notify_one();
  }

  void pop(T & value) {
    unique_lock<mutex> lock(mtx);
    while (data_queue.empty()) {
      cv.wait(lock);
    }
    value = data_queue.front();
    data_queue.pop();
  }
};

#endif