CXX = g++
CXXFLAGS = -std=c++17 -Wall -Wextra

all: regex_test regex_test_std

regex_test: regex_test.cpp
	$(CXX) $(CXXFLAGS) -o regex_test regex_test.cpp -lpcre2-8

regex_test_std: regex_test_std.cpp
	$(CXX) $(CXXFLAGS) -o regex_test_std regex_test_std.cpp

test: regex_test
	@echo "=== PCRE2 version (CORRECT) ==="
	./regex_test

test-std: regex_test_std
	@echo "=== std::regex version (LIMITED) ==="
	./regex_test_std

clean:
	rm -f regex_test regex_test_std

.PHONY: all test test-std clean
