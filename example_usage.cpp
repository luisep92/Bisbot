/**
 * EJEMPLO DE USO: Unicode Pattern Validator
 *
 * Este ejemplo muestra cómo usar el validador en un contexto real
 */

#include "unicode_pattern_validator.h"
#include <iostream>
#include <vector>

using namespace unicode_validator;

int main() {
    std::cout << "=== Ejemplo de Uso: Unicode Pattern Validator ===" << std::endl;
    std::cout << std::endl;

    // Casos de prueba reales
    std::vector<std::string> test_inputs = {
        "d:_i:1_ABC",              // ✓ válido
        "d:_n:user-123_data",      // ✓ válido
        "d:_n:Z_español",          // ✓ válido (Unicode permitido)
        "d:_n:Z_😀",               // ✓ válido (emoji permitido)
        "d:_n:Z_؀",                // ✗ inválido (U+0600 es Cf)
        "d:_n:Z_ABC ",             // ✗ inválido (espacio al final)
        "d:_i:0_ABC",              // ✗ inválido (no puede empezar con 0)
        "d:_n:test_hello world",   // ✗ inválido (espacio en el texto)
    };

    std::cout << "Validando " << test_inputs.size() << " inputs..." << std::endl;
    std::cout << std::string(60, '-') << std::endl;

    for (const auto& input : test_inputs) {
        bool is_valid = validate_pattern(input);

        std::cout << "Input: \"" << input << "\"" << std::endl;
        std::cout << "  → " << (is_valid ? "✓ VÁLIDO" : "✗ INVÁLIDO") << std::endl;
        std::cout << std::endl;
    }

    std::cout << std::string(60, '-') << std::endl;
    std::cout << std::endl;

    // Ejemplo de uso en un procesador de datos
    std::cout << "=== Simulación: Procesador de Datos ===" << std::endl;
    std::cout << std::endl;

    std::vector<std::string> data_stream = {
        "d:_i:42_HelloWorld",
        "d:_n:product-A_widget",
        "d:_n:test_bad data",      // este fallará
        "d:_i:99_valid",
        "d:_n:unicode_日本語",
    };

    int processed = 0;
    int rejected = 0;

    for (const auto& data : data_stream) {
        if (validate_pattern(data)) {
            std::cout << "[ACCEPTED] " << data << std::endl;
            processed++;
            // Aquí procesarías el dato válido
        } else {
            std::cout << "[REJECTED] " << data << " (formato inválido)" << std::endl;
            rejected++;
            // Aquí manejarías el error
        }
    }

    std::cout << std::endl;
    std::cout << "Resumen:" << std::endl;
    std::cout << "  Procesados: " << processed << std::endl;
    std::cout << "  Rechazados: " << rejected << std::endl;
    std::cout << "  Total: " << data_stream.size() << std::endl;

    std::cout << std::endl;
    std::cout << "=== Tests Específicos: Caracteres Problemáticos ===" << std::endl;
    std::cout << std::endl;

    // Test específico para el caso reportado por el usuario
    std::string arabic_sign = "d:_n:Z_؀";
    std::cout << "Test: ARABIC NUMBER SIGN (U+0600)" << std::endl;
    std::cout << "  Input: \"" << arabic_sign << "\"" << std::endl;
    std::cout << "  Resultado: " << (validate_pattern(arabic_sign) ? "VÁLIDO" : "INVÁLIDO") << std::endl;
    std::cout << "  Esperado: INVÁLIDO (U+0600 es Cf - Format)" << std::endl;
    std::cout << "  Status: " << (validate_pattern(arabic_sign) ? "✗ FAIL" : "✓ PASS") << std::endl;
    std::cout << std::endl;

    // Test con ASCII normal
    std::string ascii_normal = "d:_n:Z_ABC";
    std::cout << "Test: ASCII normal" << std::endl;
    std::cout << "  Input: \"" << ascii_normal << "\"" << std::endl;
    std::cout << "  Resultado: " << (validate_pattern(ascii_normal) ? "VÁLIDO" : "INVÁLIDO") << std::endl;
    std::cout << "  Esperado: VÁLIDO" << std::endl;
    std::cout << "  Status: " << (validate_pattern(ascii_normal) ? "✓ PASS" : "✗ FAIL") << std::endl;
    std::cout << std::endl;

    // Test con ZERO WIDTH SPACE (invisible pero Cf)
    std::string zero_width = "d:_n:Z_\u200B";
    std::cout << "Test: ZERO WIDTH SPACE (U+200B)" << std::endl;
    std::cout << "  Input: \"d:_n:Z_[ZERO_WIDTH_SPACE]\"" << std::endl;
    std::cout << "  Resultado: " << (validate_pattern(zero_width) ? "VÁLIDO" : "INVÁLIDO") << std::endl;
    std::cout << "  Esperado: INVÁLIDO (U+200B es Cf - Format)" << std::endl;
    std::cout << "  Status: " << (validate_pattern(zero_width) ? "✗ FAIL" : "✓ PASS") << std::endl;
    std::cout << std::endl;

    // Demostración de por qué std::regex no funciona
    std::cout << "=== Por qué std::regex NO funciona ===" << std::endl;
    std::cout << std::endl;
    std::cout << "std::regex NO soporta:" << std::endl;
    std::cout << "  • \\p{Cc} (Control characters)" << std::endl;
    std::cout << "  • \\p{Cf} (Format characters)" << std::endl;
    std::cout << "  • \\p{Z} (Separator characters)" << std::endl;
    std::cout << std::endl;
    std::cout << "Intentos fallidos:" << std::endl;
    std::cout << "  1. [^\\\\x00-\\\\x1F\\\\x7F\\\\s]+ → No cubre Cf como U+0600" << std::endl;
    std::cout << "  2. [^\\\\p{Cc}\\\\p{Cf}\\\\p{Z}]+ → std::regex no reconoce \\\\p{}" << std::endl;
    std::cout << std::endl;
    std::cout << "Solución correcta:" << std::endl;
    std::cout << "  → Implementación manual con validación Unicode (este código)" << std::endl;
    std::cout << "  → O usar ICU / Boost.Regex / PCRE2 (requieren librerías externas)" << std::endl;

    return 0;
}
