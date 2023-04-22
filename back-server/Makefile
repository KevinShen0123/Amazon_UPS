# Compiler and linker
CXX = g++
PROTOC = protoc

# Compiler and linker flags
CXXFLAGS = -std=c++11 -Wall
LDFLAGS = -lprotobuf -lpthread -lpqxx

# Target executable
TARGET = my_project

# Source files
PROTO_SRCS = $(wildcard *.proto)
CPP_SRCS = $(wildcard *.cpp)

# Object files
PROTO_OBJS = $(patsubst %.proto,%.pb.o,$(PROTO_SRCS))
CPP_OBJS = $(patsubst %.cpp,%.o,$(CPP_SRCS))
OBJS = $(PROTO_OBJS) $(CPP_OBJS)

# Default rule
all: $(TARGET)

# Linking
$(TARGET): $(OBJS)
	$(CXX) -o $@ $^ $(LDFLAGS)

# Compiling C++ source files
%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Compiling protocol buffer files
%.pb.o: %.proto
	$(PROTOC) --cpp_out=. $<
	$(CXX) $(CXXFLAGS) -c $*.pb.cc -o $@

# Clean rule
clean:
	rm -f *.o *.pb.cc *.pb.h $(TARGET)

.PHONY: all clean