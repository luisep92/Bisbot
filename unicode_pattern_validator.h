#ifndef UNICODE_PATTERN_VALIDATOR_H
#define UNICODE_PATTERN_VALIDATOR_H

/**
 * UNICODE PATTERN VALIDATOR
 *
 * Valida el patrón: d:_(i:[1-9][0-9]*|n:[a-zA-Z0-9-]+)_[^\p{Cc}\p{Cf}\p{Z}]+
 *
 * Uso:
 *   #include "unicode_pattern_validator.h"
 *
 *   std::string input = "d:_n:Z_ABC";
 *   if (validate_pattern(input)) {
 *       // válido
 *   }
 */

#include <string>
#include <cstdint>

namespace unicode_validator {

/**
 * Verifica si un codepoint Unicode es un carácter de control (Cc)
 * @param cp Codepoint Unicode (UTF-32)
 * @return true si es categoría Cc
 */
inline bool is_control_char(char32_t cp) {
    return (cp <= 0x1F) || (cp >= 0x7F && cp <= 0x9F);
}

/**
 * Verifica si un codepoint Unicode es un carácter de formato (Cf)
 * @param cp Codepoint Unicode (UTF-32)
 * @return true si es categoría Cf
 */
inline bool is_format_char(char32_t cp) {
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
 * Verifica si un codepoint Unicode es un separador (Z)
 * @param cp Codepoint Unicode (UTF-32)
 * @return true si es categoría Z (Zs, Zl, Zp)
 */
inline bool is_separator_char(char32_t cp) {
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
 * Convierte una secuencia UTF-8 a codepoint UTF-32
 * @param str String UTF-8
 * @param pos Posición actual (se incrementa al siguiente carácter)
 * @return Codepoint Unicode
 */
inline char32_t utf8_to_codepoint(const std::string& str, size_t& pos) {
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

/**
 * Valida el patrón completo: d:_(i:[1-9][0-9]*|n:[a-zA-Z0-9-]+)_[^\p{Cc}\p{Cf}\p{Z}]+
 *
 * @param input String UTF-8 a validar
 * @return true si cumple con el patrón, false en caso contrario
 */
inline bool validate_pattern(const std::string& input) {
    size_t pos = 0;

    // 1. Verificar prefijo "d:_"
    if (input.length() < 3 || input.substr(0, 3) != "d:_") {
        return false;
    }
    pos = 3;

    // 2. Verificar (i:[1-9][0-9]*|n:[a-zA-Z0-9-]+)
    if (pos >= input.length()) return false;

    if (input[pos] == 'i') {
        // Opción 1: i:[1-9][0-9]*
        pos++;
        if (pos >= input.length() || input[pos] != ':') return false;
        pos++;
        if (pos >= input.length() || input[pos] < '1' || input[pos] > '9') return false;
        pos++;

        while (pos < input.length() && input[pos] >= '0' && input[pos] <= '9') {
            pos++;
        }
    } else if (input[pos] == 'n') {
        // Opción 2: n:[a-zA-Z0-9-]+
        pos++;
        if (pos >= input.length() || input[pos] != ':') return false;
        pos++;

        if (pos >= input.length()) return false;
        size_t start = pos;
        while (pos < input.length() &&
               ((input[pos] >= 'a' && input[pos] <= 'z') ||
                (input[pos] >= 'A' && input[pos] <= 'Z') ||
                (input[pos] >= '0' && input[pos] <= '9') ||
                input[pos] == '-')) {
            pos++;
        }
        if (pos == start) return false;
    } else {
        return false;
    }

    // 3. Verificar separador "_"
    if (pos >= input.length() || input[pos] != '_') return false;
    pos++;

    // 4. Verificar [^\p{Cc}\p{Cf}\p{Z}]+ (uno o más caracteres válidos)
    if (pos >= input.length()) return false;

    size_t start = pos;
    while (pos < input.length()) {
        char32_t cp = utf8_to_codepoint(input, pos);

        if (is_control_char(cp) || is_format_char(cp) || is_separator_char(cp)) {
            return false;
        }
    }

    return pos > start;
}

} // namespace unicode_validator

#endif // UNICODE_PATTERN_VALIDATOR_H
