#ifndef _MYEXCEPTION_HPP_
#define _MYEXCEPTION_HPP_

#include <string>
#include <stdexcept>

class MyException: public std::runtime_error {
public:
    MyException(std::string msg): std::runtime_error(msg) {}
    MyException(const char * msg): std::runtime_error(msg) {}
    ~MyException() noexcept {};
};



#endif