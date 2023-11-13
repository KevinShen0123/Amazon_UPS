CXX = g++
CXXFLAGS = -std=c++17 -Wall -Wextra -Werror

SRC = client.cpp socket.cpp
OBJ = $(SRC:.cpp=.o)
TARGET = client

all: $(TARGET)

$(TARGET): $(OBJ)
	$(CXX) $(CXXFLAGS) -o $@ $^

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $<

.PHONY: clean
clean:
	rm -rf $(OBJ) $(TARGET)
