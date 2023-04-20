CC=g++
CFLAGS=-g -O0
EXTRAFLAGS=-lpqxx -lpq -lpthread

all: back
back:interact.cpp bufferProcessing.cpp querys.cpp 
	$(CC) $(CFLAGS) -o back interact.cpp bufferProcessing.cpp querys.cpp $(EXTRAFLAGS)
clean:
	rm -f *~ *.o back

clobber:
	rm -f *~ *.o
