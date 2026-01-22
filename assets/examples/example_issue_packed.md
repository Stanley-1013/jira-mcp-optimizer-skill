# PROJ-123 — Login shows 500 error instead of friendly message for wrong password

## Meta
- **Type**: Bug
- **Status**: In Progress
- **Priority**: High
- **Assignee**: John Doe
- **Reporter**: Jane Smith
- **Created**: 2024-01-15
- **Updated**: 2024-01-18
- **Labels**: login, authentication, critical
- **Components**: Authentication, API
- **Fix Versions**: 1.2.0

## Description
## Summary
When users enter incorrect password during login, the system shows a generic HTTP 500 error instead of a user-friendly error message.

## Steps to Reproduce
1. Navigate to /login
2. Enter a valid email address
3. Enter an incorrect password
4. Click the Login button

## Expected Behavior
A friendly error message should appear: "Invalid email or password. Please try again."

## Actual Behavior
The page shows a generic HTTP 500 Internal Server Error page.

## Environment
• Browser: Chrome 120.0.6099.109
• OS: macOS 14.2
• App Version: 2.3.1

## Recent Comments

**John Doe** (2024-01-16):
Started investigating. The error appears to be in the AuthController.login() method - the exception handler is not catching InvalidCredentialsException properly.

**John Doe** (2024-01-17):
Root cause confirmed. The @ExceptionHandler annotation was missing for InvalidCredentialsException. Working on the fix now.

---

## Comparison: Raw vs Packed

| Metric | Raw JSON | Packed MD | Savings |
|--------|----------|-----------|---------|
| Characters | ~12,500 | ~1,800 | **86%** |
| Lines | ~450 | ~45 | **90%** |
| Tokens (est.) | ~3,000 | ~400 | **87%** |

### What's Preserved
- Issue key and summary
- All essential metadata (type, status, priority, assignee, etc.)
- Full description content (converted from ADF to plain text)
- Recent comments (last 3)
- Labels, components, fix versions

### What's Removed
- API URLs and self-references
- Avatar URLs
- Duplicate nested objects
- Internal IDs
- Unnecessary metadata (workratio, aggregates, etc.)
- Full comment history (only last 3 shown)
- Detailed transition configurations

---

## Usage

```bash
# Generate this packed format from raw JSON
python scripts/pack_issue.py assets/examples/example_issue_raw.json

# Or from stdin
cat issue.json | python scripts/pack_issue.py
```

This packed format is ideal for:
1. **LLM Context** - Minimal tokens while preserving all necessary information
2. **Quick Review** - Human-readable at a glance
3. **Documentation** - Easy to include in reports or discussions
4. **Comparison** - Clear diff between issues
