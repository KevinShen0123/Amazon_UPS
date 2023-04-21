CXX = g++
PROTOC = protoc

# Directories
SRC_DIR = .
INCLUDE_DIR = .
BUILD_DIR = .

# Compiler and linker flags
CXXFLAGS = -std=c++11 -I$(INCLUDE_DIR) -Wall
LDFLAGS = -lprotobuf

# Target executable
TARGET = $(BUILD_DIR)/interact

# Source files
PROTO_SRCS = $(wildcard $(SRC_DIR)/*.proto)
CPP_SRCS = $(wildcard $(SRC_DIR)/*.cpp)

# Object files
PROTO_OBJS = $(patsubst $(SRC_DIR)/%.proto,$(BUILD_DIR)/%.pb.o,$(PROTO_SRCS))
CPP_OBJS = $(patsubst $(SRC_DIR)/%.cpp,$(BUILD_DIR)/%.o,$(CPP_SRCS))
OBJS = $(PROTO_OBJS) $(CPP_OBJS)

# Default rule
all: $(TARGET)

# Linking
$(TARGET): $(OBJS)
	$(CXX) -o $@ $^ $(LDFLAGS)

# Compiling C++ source files
$(BUILD_DIR)/%.o: $(SRC_DIR)/%.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Compiling protocol buffer files
$(BUILD_DIR)/%.pb.o: $(SRC_DIR)/%.proto
	$(PROTOC) -I$(SRC_DIR) --cpp_out=$(INCLUDE_DIR) $<
	$(CXX) $(CXXFLAGS) -c $(INCLUDE_DIR)/$*.pb.cc -o $@

# Clean rule
clean:
	rm -f $(BUILD_DIR)/*.o $(INCLUDE_DIR)/*.pb.cc $(INCLUDE_DIR)/*.pb.h $(TARGET)

.PHONY: all clean