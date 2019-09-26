target : main test

CFLAGS = -g

main : main.o kdtree.o config.h
	g++ $(CFLAGS) main.o kdtree.o -o main -lmysqlclient

test : test.o kdtree.o
	g++ $(CFLAGS) test.o kdtree.o -o test

main.o : main.cpp
	g++ $(CFLAGS) main.cpp -o main.o -c -I /usr/include/ 

kdtree.o : kdtree.cpp kdtree.h
	g++ $(CFLAGS) kdtree.cpp -o kdtree.o -c

test.o : test.cpp
	g++ $(CFLAGS) test.cpp -o test.o -c

clean :
	rm *.o
	rm main test

