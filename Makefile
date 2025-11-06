CXX = g++
CXXFLAGS = -std=c++17 -Wall -Wextra
LDFLAGS = -lpcre2-8

TARGET = regex_test
SRC = regex_test.cpp

all: $(TARGET)

$(TARGET): $(SRC)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(SRC) $(LDFLAGS)

test: $(TARGET)
	./$(TARGET)

clean:
	rm -f $(TARGET)

.PHONY: all test clean
