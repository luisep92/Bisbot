# Makefile para Unicode Pattern Validator Research

CXX = g++
CXXFLAGS = -std=c++17 -Wall -Wextra -O2

# Targets
TARGETS = regex_solution regex_research example_usage

# Default target
all: $(TARGETS)

# Build targets
regex_solution: regex_solution.cpp unicode_pattern_validator.h
	$(CXX) $(CXXFLAGS) -o $@ $<

regex_research: regex_research.cpp
	$(CXX) $(CXXFLAGS) -o $@ $<

example_usage: example_usage.cpp unicode_pattern_validator.h
	$(CXX) $(CXXFLAGS) -o $@ $<

# Run tests
test: regex_solution
	@echo "========================================"
	@echo "Ejecutando tests completos..."
	@echo "========================================"
	./regex_solution

# Run example
example: example_usage
	@echo "========================================"
	@echo "Ejecutando ejemplo de uso..."
	@echo "========================================"
	./example_usage

# Run all tests and examples
run-all: test example
	@echo ""
	@echo "========================================"
	@echo "✓ Todos los tests completados"
	@echo "========================================"

# Clean
clean:
	rm -f $(TARGETS)

# Help
help:
	@echo "Unicode Pattern Validator - Makefile"
	@echo ""
	@echo "Targets disponibles:"
	@echo "  make           - Compila todos los programas"
	@echo "  make test      - Ejecuta los tests completos"
	@echo "  make example   - Ejecuta el ejemplo de uso"
	@echo "  make run-all   - Ejecuta tests y ejemplo"
	@echo "  make clean     - Elimina los ejecutables"
	@echo "  make help      - Muestra esta ayuda"
	@echo ""
	@echo "Archivos:"
	@echo "  regex_solution.cpp          - Solución completa con tests"
	@echo "  regex_research.cpp          - Primera versión de research"
	@echo "  example_usage.cpp           - Ejemplo de uso práctico"
	@echo "  unicode_pattern_validator.h - Header reutilizable"
	@echo "  REGEX_RESEARCH.md           - Documentación completa"

.PHONY: all test example run-all clean help
