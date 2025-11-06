#include <iostream>
#include <string>
#include <vector>
#include <regex>
#include <cassert>
#include <iomanip>

// Para este research vamos a usar diferentes enfoques
// Approach 1: std::regex básico con aproximación de caracteres
// Approach 2: Implementación manual que verifica Unicode categories

struct TestCase {
    std::string input;
    bool should_match;
    std::string description;
};

// Función auxiliar para verificar si un codepoint es de categoría Cc (Control)
bool is_control_char(char32_t cp) {
    return (cp <= 0x1F) || (cp >= 0x7F && cp <= 0x9F);
}

// Función auxiliar para verificar si un codepoint es de categoría Cf (Format)
bool is_format_char(char32_t cp) {
    // Rangos principales de caracteres de formato Unicode
    return (cp == 0x00AD) || // SOFT HYPHEN
           (cp >= 0x0600 && cp <= 0x0605) || // ARABIC NUMBER SIGN, etc.
           (cp >= 0x061C && cp <= 0x061C) || // ARABIC LETTER MARK
           (cp >= 0x06DD && cp <= 0x06DD) || // ARABIC END OF AYAH
           (cp >= 0x070F && cp <= 0x070F) || // SYRIAC ABBREVIATION MARK
           (cp >= 0x08E2 && cp <= 0x08E2) || // ARABIC DISPUTED END OF AYAH
           (cp >= 0x180E && cp <= 0x180E) || // MONGOLIAN VOWEL SEPARATOR
           (cp >= 0x200B && cp <= 0x200F) || // ZERO WIDTH SPACE, etc.
           (cp >= 0x202A && cp <= 0x202E) || // Various directional formatting
           (cp >= 0x2060 && cp <= 0x2064) || // WORD JOINER, etc.
           (cp >= 0x2066 && cp <= 0x206F) || // Various directional and deprecated
           (cp >= 0xFEFF && cp <= 0xFEFF) || // ZERO WIDTH NO-BREAK SPACE
           (cp >= 0xFFF9 && cp <= 0xFFFB) || // Interlinear annotation
           (cp >= 0x110BD && cp <= 0x110BD) || // KAITHI NUMBER SIGN
           (cp >= 0x110CD && cp <= 0x110CD) || // KAITHI NUMBER SIGN
           (cp >= 0x13430 && cp <= 0x13438) || // Egyptian Hieroglyph Format Controls
           (cp >= 0x1BCA0 && cp <= 0x1BCA3) || // Shorthand Format Controls
           (cp >= 0x1D173 && cp <= 0x1D17A) || // Musical Symbols
           (cp >= 0xE0001 && cp <= 0xE0001) || // Language Tag
           (cp >= 0xE0020 && cp <= 0xE007F);   // Tag characters
}

// Función auxiliar para verificar si un codepoint es de categoría Z (Separator)
bool is_separator_char(char32_t cp) {
    return (cp == 0x0020) || // SPACE
           (cp >= 0x00A0 && cp <= 0x00A0) || // NO-BREAK SPACE
           (cp >= 0x1680 && cp <= 0x1680) || // OGHAM SPACE MARK
           (cp >= 0x2000 && cp <= 0x200A) || // Various spaces
           (cp >= 0x2028 && cp <= 0x2029) || // LINE SEPARATOR, PARAGRAPH SEPARATOR
           (cp >= 0x202F && cp <= 0x202F) || // NARROW NO-BREAK SPACE
           (cp >= 0x205F && cp <= 0x205F) || // MEDIUM MATHEMATICAL SPACE
           (cp >= 0x3000 && cp <= 0x3000);   // IDEOGRAPHIC SPACE
}

// Convertir UTF-8 a UTF-32 codepoint
char32_t utf8_to_codepoint(const std::string& str, size_t& pos) {
    unsigned char c = str[pos];
    char32_t cp = 0;

    if (c <= 0x7F) {
        cp = c;
        pos += 1;
    } else if ((c & 0xE0) == 0xC0) {
        cp = ((c & 0x1F) << 6) | (str[pos + 1] & 0x3F);
        pos += 2;
    } else if ((c & 0xF0) == 0xE0) {
        cp = ((c & 0x0F) << 12) | ((str[pos + 1] & 0x3F) << 6) | (str[pos + 2] & 0x3F);
        pos += 3;
    } else if ((c & 0xF8) == 0xF0) {
        cp = ((c & 0x07) << 18) | ((str[pos + 1] & 0x3F) << 12) |
             ((str[pos + 2] & 0x3F) << 6) | (str[pos + 3] & 0x3F);
        pos += 4;
    }

    return cp;
}

// Verificar manualmente el patrón completo
bool manual_match(const std::string& input) {
    size_t pos = 0;

    // Verificar "d:_"
    if (input.substr(0, 3) != "d:_") return false;
    pos = 3;

    // Verificar (i:[1-9][0-9]*|n:[a-zA-Z0-9-]+)
    if (pos >= input.length()) return false;

    if (input[pos] == 'i') {
        pos++; // 'i'
        if (pos >= input.length() || input[pos] != ':') return false;
        pos++; // ':'
        if (pos >= input.length() || input[pos] < '1' || input[pos] > '9') return false;
        pos++; // primer dígito [1-9]
        // [0-9]* (cero o más dígitos)
        while (pos < input.length() && input[pos] >= '0' && input[pos] <= '9') {
            pos++;
        }
    } else if (input[pos] == 'n') {
        pos++; // 'n'
        if (pos >= input.length() || input[pos] != ':') return false;
        pos++; // ':'
        // [a-zA-Z0-9-]+ (uno o más)
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
        return false;
    }

    // Verificar "_"
    if (pos >= input.length() || input[pos] != '_') return false;
    pos++;

    // Verificar [^\p{Cc}\p{Cf}\p{Z}]+ (uno o más caracteres que NO sean control, format, o separator)
    if (pos >= input.length()) return false;

    size_t start = pos;
    while (pos < input.length()) {
        size_t current_pos = pos;
        char32_t cp = utf8_to_codepoint(input, pos);

        if (is_control_char(cp) || is_format_char(cp) || is_separator_char(cp)) {
            // Este carácter no es válido
            return false;
        }
    }

    return pos > start; // debe haber al menos un carácter válido
}

void run_test(const TestCase& test, int test_num) {
    bool result = manual_match(test.input);

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
    std::cout << "=== Regex Research Test Suite ===" << std::endl;
    std::cout << "Target pattern: d:_(i:[1-9][0-9]*|n:[a-zA-Z0-9-]+)_[^\\p{Cc}\\p{Cf}\\p{Z}]+" << std::endl;
    std::cout << std::endl;

    std::vector<TestCase> tests = {
        // Tests básicos con 'i' (integer)
        {"d:_i:1_ABC", true, "Basic integer ID with ASCII text"},
        {"d:_i:123_test", true, "Multi-digit integer ID"},
        {"d:_i:999_xyz", true, "Large integer ID"},

        // Tests básicos con 'n' (name)
        {"d:_n:Z_ABC", true, "Single letter name with ASCII text"},
        {"d:_n:test_hello", true, "Multi-letter name"},
        {"d:_n:abc123_data", true, "Alphanumeric name"},
        {"d:_n:my-name_value", true, "Name with hyphen"},

        // Tests con caracteres Unicode válidos (no Cc, Cf, Z)
        {"d:_n:Z_😀", true, "Emoji should be allowed"},
        {"d:_n:Z_日本語", true, "Japanese characters should be allowed"},
        {"d:_n:Z_español", true, "Spanish characters should be allowed"},
        {"d:_n:Z_Ω", true, "Greek letter should be allowed"},
        {"d:_n:Z_中文", true, "Chinese characters should be allowed"},

        // Tests que DEBEN FALLAR - Caracteres de control (Cc)
        {"d:_n:Z_ABC\x01", false, "Control character (0x01) should fail"},
        {"d:_n:Z_ABC\x1F", false, "Control character (0x1F) should fail"},
        {"d:_n:Z_ABC\x7F", false, "Control character (DEL) should fail"},

        // Tests que DEBEN FALLAR - Caracteres de formato (Cf)
        {"d:_n:Z_؀", false, "ARABIC NUMBER SIGN (U+0600, Cf) should fail"},
        {"d:_n:Z_\u200B", false, "ZERO WIDTH SPACE (U+200B, Cf) should fail"},
        {"d:_n:Z_\uFEFF", false, "ZERO WIDTH NO-BREAK SPACE (U+FEFF, Cf) should fail"},
        {"d:_n:Z_ABC\u061C", false, "ARABIC LETTER MARK (U+061C, Cf) should fail"},

        // Tests que DEBEN FALLAR - Separadores (Z)
        {"d:_n:Z_ ", false, "Space (U+0020) should fail"},
        {"d:_n:Z_ABC ", false, "Trailing space should fail"},
        {"d:_n:Z_\u00A0", false, "NO-BREAK SPACE (U+00A0) should fail"},
        {"d:_n:Z_\u2000", false, "EN QUAD (U+2000, Zs) should fail"},
        {"d:_n:Z_\u3000", false, "IDEOGRAPHIC SPACE (U+3000) should fail"},

        // Tests de formato incorrecto
        {"d:_i:0_ABC", false, "Integer starting with 0 should fail"},
        {"d:_n:_ABC", false, "Empty name should fail"},
        {"d:_i:_ABC", false, "Missing integer should fail"},
        {"d:_ABC", false, "Missing ID section should fail"},
        {"d:_n:Z", false, "Missing final section should fail"},
        {"d:_n:Z_", false, "Empty final section should fail"},

        // Tests edge case
        {"d:_i:1_A", true, "Minimal valid input with integer"},
        {"d:_n:a_B", true, "Minimal valid input with name"},
        {"d:_n:123_ABC", true, "Name starting with digit"},
        {"d:_n:a-b-c_test", true, "Multiple hyphens in name"},

        // Tests con múltiples caracteres Unicode
        {"d:_n:Z_ABC日本", true, "Mixed ASCII and Unicode"},
        {"d:_n:Z_🎨🎭🎪", true, "Multiple emojis"},

        // Tests con caracteres especiales válidos
        {"d:_n:Z_@#$%", true, "Special ASCII characters (not control/separator)"},
        {"d:_n:Z_[]{}()", true, "Brackets and braces"},
        {"d:_n:Z_+=*&^", true, "Math and logic symbols"},
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

    std::cout << "=== Test Summary ===" << std::endl;
    std::cout << "Total: " << tests.size() << std::endl;
    std::cout << "Passed: " << passed << std::endl;
    std::cout << "Failed: " << failed << std::endl;

    if (failed == 0) {
        std::cout << std::endl << "✓ ALL TESTS PASSED!" << std::endl;
        return 0;
    } else {
        std::cout << std::endl << "✗ SOME TESTS FAILED!" << std::endl;
        return 1;
    }
}
