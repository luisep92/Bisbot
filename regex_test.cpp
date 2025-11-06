#define PCRE2_CODE_UNIT_WIDTH 8
#include <iostream>
#include <string>
#include <vector>
#include <pcre2.h>

// Original XML regex: d:(i:[1-9][0-9]*|n:[a-zA-Z0-9-]+)[^\p{Cc}\p{Cf}\p{Z}]+
// PCRE2 supports Unicode properties directly, so we use the same pattern
// Adding $ to match end of string (full string match)
const char* PATTERN = "^d:(i:[1-9][0-9]*|n:[a-zA-Z0-9-]+)[^\\p{Cc}\\p{Cf}\\p{Z}]+$";

struct TestCase {
    std::string input;
    bool should_match;
    std::string description;
};

bool test_regex(const std::string& input) {
    int errornumber;
    PCRE2_SIZE erroroffset;

    pcre2_code* re = pcre2_compile(
        (PCRE2_SPTR)PATTERN,
        PCRE2_ZERO_TERMINATED,
        PCRE2_UTF | PCRE2_UCP,
        &errornumber,
        &erroroffset,
        NULL
    );

    if (re == NULL) {
        std::cerr << "Regex compilation failed\n";
        return false;
    }

    pcre2_match_data* match_data = pcre2_match_data_create_from_pattern(re, NULL);

    int rc = pcre2_match(
        re,
        (PCRE2_SPTR)input.c_str(),
        input.length(),
        0,
        0,
        match_data,
        NULL
    );

    bool matched = rc >= 0;

    pcre2_match_data_free(match_data);
    pcre2_code_free(re);

    return matched;
}

int main() {
    std::vector<TestCase> tests = {
        // Basic positive cases
        {"d:i:1test", true, "Integer identifier with text"},
        {"d:i:123abc", true, "Multi-digit integer with text"},
        {"d:n:abc_def", true, "Named identifier with underscore"},
        {"d:n:test-123_xyz", true, "Named identifier with dash and underscore"},

        // Critical test case: d:n:Z with valid continuation
        {"d:n:Z_ABC", true, "d:n:Z_ABC (must match)"},

        // Negative cases - control characters (Cc)
        {std::string("d:i:1") + char(0x01) + "test", false, "Contains control char (0x01)"},
        {std::string("d:n:abc") + char(0x1F) + "def", false, "Contains control char (0x1F)"},

        // Critical test case: format characters must be rejected
        {std::string("d:n:Z_") + "\xD8\x80", false, "d:n:Z_ + U+0600 (must NOT match - format char)"},

        // Negative cases - separator characters (Z)
        {"d:i:1 test", false, "Contains space (Zs)"},
        {"d:n:abc\xE2\x80\xA8""def", false, "Contains line separator U+2028 (Zl)"},
        {"d:n:abc\xE2\x80\xA9""def", false, "Contains paragraph separator U+2029 (Zp)"},

        // Edge cases
        {"d:i:0abc", false, "Integer starts with 0"},
        {"d:i:abc", false, "Not a valid integer"},
        {"d:n:_abc", false, "Named identifier starts with underscore"},
        {"d:i:1_", true, "Minimal integer case with trailing char"},
        {"d:n:a_", true, "Minimal named case with underscore"},

        // Invalid prefixes
        {"d:x:1test", false, "Invalid prefix x"},
        {"i:1test", false, "Missing d: prefix"},

        // Long valid strings
        {"d:n:test_" + std::string(250, 'x'), true, "Long valid string"},
    };

    std::cout << "Testing regex pattern: " << PATTERN << "\n\n";

    int passed = 0;
    int failed = 0;

    for (const auto& test : tests) {
        bool result = test_regex(test.input);
        bool success = (result == test.should_match);

        if (success) {
            passed++;
            std::cout << "[PASS] ";
        } else {
            failed++;
            std::cout << "[FAIL] ";
        }

        std::cout << test.description << "\n";
        std::cout << "       Expected: " << (test.should_match ? "match" : "no match");
        std::cout << " | Got: " << (result ? "match" : "no match") << "\n\n";
    }

    std::cout << "Results: " << passed << " passed, " << failed << " failed\n";

    return failed > 0 ? 1 : 0;
}
