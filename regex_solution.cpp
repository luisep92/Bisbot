/**
 * SOLUCIÓN CORRECTA PARA LA EXPRESIÓN REGULAR
 *
 * Patrón original (XML/Unicode): d:_(i:[1-9][0-9]*|n:[a-zA-Z0-9-]+)_[^\p{Cc}\p{Cf}\p{Z}]+
 *
 * PROBLEMA: std::regex de C++ NO soporta propiedades Unicode (\p{Cc}, \p{Cf}, \p{Z})
 *
 * SOLUCIONES POSIBLES:
 * 1. Implementación manual (esta solución) ✓
 * 2. Usar ICU (International Components for Unicode)
 * 3. Usar Boost.Regex con Unicode
 * 4. Usar PCRE2
 *
 * Esta implementación usa validación manual para verificar correctamente
 * las categorías Unicode que deben ser excluidas.
 */

#include <iostream>
#include <string>
#include <vector>
#include <cassert>

/**
 * Verifica si un codepoint es de categoría Cc (Control Characters)
 * Incluye: 0x00-0x1F, 0x7F-0x9F
 */
bool is_control_char(char32_t cp) {
    return (cp <= 0x1F) || (cp >= 0x7F && cp <= 0x9F);
}

/**
 * Verifica si un codepoint es de categoría Cf (Format Characters)
 * Incluye caracteres invisibles de formato como:
 * - ZERO WIDTH SPACE (U+200B)
 * - ARABIC NUMBER SIGN (U+0600) ← Este es el que falla "d:_n:Z_؀"
 * - SOFT HYPHEN (U+00AD)
 * - ZERO WIDTH NO-BREAK SPACE (U+FEFF)
 * - Etc.
 */
bool is_format_char(char32_t cp) {
    return (cp == 0x00AD) ||
           (cp >= 0x0600 && cp <= 0x0605) ||
           (cp >= 0x061C && cp <= 0x061C) ||
           (cp >= 0x06DD && cp <= 0x06DD) ||
           (cp >= 0x070F && cp <= 0x070F) ||
           (cp >= 0x08E2 && cp <= 0x08E2) ||
           (cp >= 0x180E && cp <= 0x180E) ||
           (cp >= 0x200B && cp <= 0x200F) ||
           (cp >= 0x202A && cp <= 0x202E) ||
           (cp >= 0x2060 && cp <= 0x2064) ||
           (cp >= 0x2066 && cp <= 0x206F) ||
           (cp >= 0xFEFF && cp <= 0xFEFF) ||
           (cp >= 0xFFF9 && cp <= 0xFFFB) ||
           (cp >= 0x110BD && cp <= 0x110BD) ||
           (cp >= 0x110CD && cp <= 0x110CD) ||
           (cp >= 0x13430 && cp <= 0x13438) ||
           (cp >= 0x1BCA0 && cp <= 0x1BCA3) ||
           (cp >= 0x1D173 && cp <= 0x1D17A) ||
           (cp >= 0xE0001 && cp <= 0xE0001) ||
           (cp >= 0xE0020 && cp <= 0xE007F);
}

/**
 * Verifica si un codepoint es de categoría Z (Separator Characters)
 * Incluye Zs (space), Zl (line separator), Zp (paragraph separator)
 * - SPACE (U+0020)
 * - NO-BREAK SPACE (U+00A0)
 * - IDEOGRAPHIC SPACE (U+3000)
 * - Etc.
 */
bool is_separator_char(char32_t cp) {
    return (cp == 0x0020) ||
           (cp >= 0x00A0 && cp <= 0x00A0) ||
           (cp >= 0x1680 && cp <= 0x1680) ||
           (cp >= 0x2000 && cp <= 0x200A) ||
           (cp >= 0x2028 && cp <= 0x2029) ||
           (cp >= 0x202F && cp <= 0x202F) ||
           (cp >= 0x205F && cp <= 0x205F) ||
           (cp >= 0x3000 && cp <= 0x3000);
}

/**
 * Convierte una secuencia UTF-8 a un codepoint UTF-32
 * y avanza el índice pos al siguiente carácter
 */
char32_t utf8_to_codepoint(const std::string& str, size_t& pos) {
    unsigned char c = str[pos];
    char32_t cp = 0;

    if (c <= 0x7F) {
        // ASCII: 1 byte
        cp = c;
        pos += 1;
    } else if ((c & 0xE0) == 0xC0) {
        // 2 bytes
        cp = ((c & 0x1F) << 6) | (str[pos + 1] & 0x3F);
        pos += 2;
    } else if ((c & 0xF0) == 0xE0) {
        // 3 bytes
        cp = ((c & 0x0F) << 12) | ((str[pos + 1] & 0x3F) << 6) | (str[pos + 2] & 0x3F);
        pos += 3;
    } else if ((c & 0xF8) == 0xF0) {
        // 4 bytes (incluyendo emojis)
        cp = ((c & 0x07) << 18) | ((str[pos + 1] & 0x3F) << 12) |
             ((str[pos + 2] & 0x3F) << 6) | (str[pos + 3] & 0x3F);
        pos += 4;
    }

    return cp;
}

/**
 * FUNCIÓN PRINCIPAL: Valida el patrón completo
 * d:_(i:[1-9][0-9]*|n:[a-zA-Z0-9-]+)_[^\p{Cc}\p{Cf}\p{Z}]+
 *
 * @param input String UTF-8 a validar
 * @return true si el string cumple con el patrón, false en caso contrario
 */
bool validate_pattern(const std::string& input) {
    size_t pos = 0;

    // 1. Verificar prefijo "d:_"
    if (input.substr(0, 3) != "d:_") return false;
    pos = 3;

    // 2. Verificar (i:[1-9][0-9]*|n:[a-zA-Z0-9-]+)
    if (pos >= input.length()) return false;

    if (input[pos] == 'i') {
        // Opción 1: i:[1-9][0-9]*
        pos++; // 'i'
        if (pos >= input.length() || input[pos] != ':') return false;
        pos++; // ':'
        if (pos >= input.length() || input[pos] < '1' || input[pos] > '9') return false;
        pos++; // primer dígito [1-9]

        // [0-9]* (cero o más dígitos adicionales)
        while (pos < input.length() && input[pos] >= '0' && input[pos] <= '9') {
            pos++;
        }
    } else if (input[pos] == 'n') {
        // Opción 2: n:[a-zA-Z0-9-]+
        pos++; // 'n'
        if (pos >= input.length() || input[pos] != ':') return false;
        pos++; // ':'

        // [a-zA-Z0-9-]+ (uno o más caracteres)
        if (pos >= input.length()) return false;
        size_t start = pos;
        while (pos < input.length() &&
               ((input[pos] >= 'a' && input[pos] <= 'z') ||
                (input[pos] >= 'A' && input[pos] <= 'Z') ||
                (input[pos] >= '0' && input[pos] <= '9') ||
                input[pos] == '-')) {
            pos++;
        }
        if (pos == start) return false; // necesita al menos un carácter
    } else {
        return false; // debe ser 'i' o 'n'
    }

    // 3. Verificar separador "_"
    if (pos >= input.length() || input[pos] != '_') return false;
    pos++;

    // 4. Verificar [^\p{Cc}\p{Cf}\p{Z}]+ (uno o más caracteres válidos)
    if (pos >= input.length()) return false;

    size_t start = pos;
    while (pos < input.length()) {
        char32_t cp = utf8_to_codepoint(input, pos);

        // Rechazar si es control, format, o separator
        if (is_control_char(cp) || is_format_char(cp) || is_separator_char(cp)) {
            return false;
        }
    }

    return pos > start; // debe haber al menos un carácter válido
}

// ============================================================================
// TESTS
// ============================================================================

struct TestCase {
    std::string input;
    bool should_match;
    std::string description;
};

void run_test(const TestCase& test, int test_num) {
    bool result = validate_pattern(test.input);

    std::cout << "Test #" << test_num << ": " << test.description << std::endl;
    std::cout << "  Input: \"" << test.input << "\"" << std::endl;
    std::cout << "  Expected: " << (test.should_match ? "MATCH" : "NO MATCH") << std::endl;
    std::cout << "  Got: " << (result ? "MATCH" : "NO MATCH") << std::endl;

    if (result == test.should_match) {
        std::cout << "  ✓ PASS" << std::endl;
    } else {
        std::cout << "  ✗ FAIL" << std::endl;
    }
    std::cout << std::endl;

    assert(result == test.should_match);
}

int main() {
    std::cout << "=== SOLUCIÓN CORRECTA: Validación de Patrón Unicode ===" << std::endl;
    std::cout << "Patrón: d:_(i:[1-9][0-9]*|n:[a-zA-Z0-9-]+)_[^\\p{Cc}\\p{Cf}\\p{Z}]+" << std::endl;
    std::cout << std::endl;

    std::vector<TestCase> tests = {
        // === CASOS REPORTADOS POR EL USUARIO ===
        {"d:_n:Z_؀", false, "CASO USUARIO: ARABIC NUMBER SIGN (U+0600) es Cf - DEBE FALLAR"},
        {"d:_n:Z_ABC", true, "CASO USUARIO: Texto ASCII normal - DEBE PASAR"},

        // === TESTS BÁSICOS ===
        {"d:_i:1_ABC", true, "Integer ID básico"},
        {"d:_i:123_test", true, "Integer ID multi-dígito"},
        {"d:_n:Z_hello", true, "Name ID con texto"},
        {"d:_n:test_data", true, "Name ID completo"},
        {"d:_n:my-name_value", true, "Name con guión"},

        // === TESTS UNICODE VÁLIDOS ===
        {"d:_n:Z_😀", true, "Emoji permitido"},
        {"d:_n:Z_日本語", true, "Japonés permitido"},
        {"d:_n:Z_español", true, "Español permitido"},
        {"d:_n:Z_Ω", true, "Griego permitido"},
        {"d:_n:Z_中文", true, "Chino permitido"},
        {"d:_n:Z_🎨🎭", true, "Múltiples emojis"},

        // === TESTS QUE DEBEN FALLAR - Control Characters (Cc) ===
        {"d:_n:Z_ABC\x01", false, "Control 0x01 rechazado"},
        {"d:_n:Z_ABC\x1F", false, "Control 0x1F rechazado"},
        {"d:_n:Z_ABC\x7F", false, "DEL rechazado"},

        // === TESTS QUE DEBEN FALLAR - Format Characters (Cf) ===
        {"d:_n:Z_\u200B", false, "ZERO WIDTH SPACE rechazado"},
        {"d:_n:Z_\uFEFF", false, "ZERO WIDTH NO-BREAK SPACE rechazado"},
        {"d:_n:Z_\u061C", false, "ARABIC LETTER MARK rechazado"},

        // === TESTS QUE DEBEN FALLAR - Separators (Z) ===
        {"d:_n:Z_ ", false, "Espacio normal rechazado"},
        {"d:_n:Z_ABC ", false, "Espacio al final rechazado"},
        {"d:_n:Z_\u00A0", false, "NO-BREAK SPACE rechazado"},
        {"d:_n:Z_\u3000", false, "IDEOGRAPHIC SPACE rechazado"},

        // === TESTS DE FORMATO ===
        {"d:_i:0_ABC", false, "Integer no puede empezar con 0"},
        {"d:_n:_ABC", false, "Name vacío"},
        {"d:_n:Z_", false, "Texto final vacío"},
        {"d:_i:1_A", true, "Mínimo válido con integer"},
        {"d:_n:a_B", true, "Mínimo válido con name"},

        // === TESTS ADICIONALES ===
        {"d:_n:Z_@#$%", true, "Símbolos ASCII especiales permitidos"},
        {"d:_n:Z_[]{}()", true, "Brackets permitidos"},
        {"d:_n:Z_ABC日本", true, "ASCII + Unicode mezclado"},
    };

    int test_num = 1;
    int passed = 0;
    int failed = 0;

    for (const auto& test : tests) {
        try {
            run_test(test, test_num);
            passed++;
        } catch (const std::exception& e) {
            std::cout << "  Exception: " << e.what() << std::endl;
            failed++;
        }
        test_num++;
    }

    std::cout << "=== RESUMEN ===" << std::endl;
    std::cout << "Total: " << tests.size() << std::endl;
    std::cout << "Pasados: " << passed << std::endl;
    std::cout << "Fallados: " << failed << std::endl;

    if (failed == 0) {
        std::cout << std::endl << "✓ ✓ ✓ TODOS LOS TESTS PASARON ✓ ✓ ✓" << std::endl;
        std::cout << std::endl << "CONCLUSIÓN: La implementación manual es correcta." << std::endl;
        std::cout << "Esta es la ÚNICA forma de validar correctamente el patrón" << std::endl;
        std::cout << "en C++ estándar sin librerías externas." << std::endl;
        return 0;
    } else {
        std::cout << std::endl << "✗ ALGUNOS TESTS FALLARON" << std::endl;
        return 1;
    }
}
