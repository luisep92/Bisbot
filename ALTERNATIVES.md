# Regex XML to C++ - Alternatives Analysis

## Question: Does PCRE2 come with C++? Is it viable without it?

**Short answer:** PCRE2 does NOT come with C++. It's an external library.

## Option 1: PCRE2 (Recommended)

**Pros:**
- Supports Unicode properties exactly as XML regex
- Pattern is identical: `[^\p{Cc}\p{Cf}\p{Z}]+`
- All test cases pass (19/19)
- Industry standard

**Cons:**
- External dependency (must install: `apt-get install libpcre2-dev`)
- Adds ~200KB to binary

**Viability:** HIGH - Best solution for production code

## Option 2: std::regex (C++ Standard Library)

**Pros:**
- No external dependencies
- Ships with C++ compiler

**Cons:**
- Does NOT support Unicode properties `\p{}`
- Cannot properly validate Unicode format/separator chars
- Only works for ASCII range
- Test results: 4/6 pass (Unicode tests fail)

**Viability:** LOW - Only if you guarantee ASCII-only input

**Example limitation:**
```cpp
// This passes but SHOULD fail (U+0600 is format char):
d:n:Z_؀  // INCORRECTLY MATCHES with std::regex

// This passes but SHOULD fail (U+2028 is line separator):
d:n:abc def  // INCORRECTLY MATCHES with std::regex
```

## Option 3: Manual Unicode Table Lookup

Write custom code to check each character against Unicode category tables.

**Pros:**
- No external regex library needed

**Cons:**
- Must maintain Unicode character tables (100+ KB of data)
- Complex implementation (500+ lines of code)
- Maintenance burden when Unicode standard updates
- Error-prone

**Viability:** VERY LOW - Not worth the effort

## Recommendation

**If you can install PCRE2:** Use it. It's the correct solution.

**If you absolutely cannot use external libs:**
- Accept that Unicode chars beyond ASCII won't be validated correctly
- Use std::regex with ASCII-only pattern
- Document the limitation clearly
- Consider if your input will ever have Unicode (if no, std::regex is fine)

## Installation

PCRE2 is available in all major package managers:
```bash
# Debian/Ubuntu
apt-get install libpcre2-dev

# MacOS
brew install pcre2

# Windows (vcpkg)
vcpkg install pcre2
```
