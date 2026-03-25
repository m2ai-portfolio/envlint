# EnvLint QA Test Report
## Feature: Schema Validation (First Feature)

**Test Date:** 2026-03-25
**Working Directory:** /home/apexaipc/projects/yce-harness/generations/metroplex-ideaforge-139
**Server Status:** Running on port 5000

---

## Test Summary

| Metric | Count |
|--------|-------|
| Total Tests | 6 |
| Passed | 6 |
| Failed | 0 |

**Overall Result: PASS**

---

## Test Results Details

### Test 1: Web Interface Loads - PASS

- Page loads successfully (HTTP 200)
- Page title is "EnvLint - Environment Validator"
- Form contains textarea for .env content
- Form contains textarea for schema
- Validate button is present
- Example links are functional

### Test 2: Valid .env Passes Validation - PASS

- Submitted valid .env with required keys
- Response: success=true, errors=[]
- Validation passed as expected

### Test 3: Missing Required Key Detected - PASS

- Submitted .env missing API_KEY
- Response: success=false
- Error: "Missing required key: API_KEY"
- Correctly detected missing key

### Test 4: Unknown Key Detected - PASS

- Submitted .env with EXTRA_KEY not in allowed list
- Response: success=false
- Error: "Unknown key not in allowed list: EXTRA_KEY"
- Correctly detected unknown key

### Test 5: Pattern Violation Detected - PASS

- Submitted DATABASE_URL with invalid pattern
- Response: success=false
- Error: "Value for DATABASE_URL does not match pattern"
- Correctly detected pattern violation

### Test 6: CLI Tool Works - PASS

**Test 6a - Valid file passes:**
- Command: python -m envlint.main --env-file /tmp/test_envlint.env --schema /tmp/test_schema.json
- Output: All validations passed\!
- Exit Code: 0

**Test 6b - Invalid file fails:**
- Command: python -m envlint.main --env-file /tmp/test_envlint_bad.env --schema /tmp/test_schema.json
- Output: Missing required key: API_KEY
- Exit Code: 1

---

## QA Sign-off: APPROVED

All Schema Validation functionality is working correctly.
No regressions detected. Feature is ready for production use.
