# Acceptance Criteria Templates

> 驗收標準 (AC) 模板，確保功能完整性和可測試性。

---

## Format Guidelines

### Gherkin Format (Recommended)

```gherkin
Given [前置條件/狀態]
When [用戶執行的動作]
Then [預期結果]
And [額外預期結果]
```

### Checklist Format

```markdown
- [ ] [可驗證的條件 1]
- [ ] [可驗證的條件 2]
- [ ] [可驗證的條件 3]
```

---

## By Feature Type

### User Authentication

```gherkin
# Login Success
Given user is on the login page
And user has a valid account
When user enters correct email and password
And clicks the login button
Then user is redirected to the dashboard
And user session is created
And last login timestamp is updated

# Login Failure - Invalid Credentials
Given user is on the login page
When user enters incorrect password
And clicks the login button
Then error message "Invalid email or password" is displayed
And user remains on the login page
And failed login attempt is logged

# Login Failure - Account Locked
Given user has 5 consecutive failed login attempts
When user attempts to login again
Then error message "Account locked. Please try again in 30 minutes" is displayed
And no further login attempts are processed
```

### CRUD Operations

```gherkin
# Create
Given user has permission to create [entity]
When user fills in all required fields
And clicks save button
Then [entity] is created successfully
And success message is displayed
And user is redirected to [entity] detail page

# Read
Given [entity] exists in the system
When user navigates to [entity] list page
Then [entity] is displayed in the list
And all relevant fields are visible

# Update
Given user has permission to edit [entity]
When user modifies [field]
And clicks save button
Then changes are saved successfully
And updated timestamp is refreshed
And audit log is created

# Delete
Given user has permission to delete [entity]
When user clicks delete button
Then confirmation dialog is displayed
When user confirms deletion
Then [entity] is removed from the system
And user is redirected to list page
```

### Search & Filter

```gherkin
# Search
Given user is on the list page
When user enters search term in the search box
And presses Enter or clicks search button
Then results matching the search term are displayed
And non-matching items are hidden
And result count is updated

# Filter
Given user is on the list page
When user selects filter option [option]
Then only items matching the filter are displayed
And filter indicator shows active filter
And clear filter option is available

# Pagination
Given there are more than [N] items
When user is on the list page
Then only first [N] items are displayed
And pagination controls are visible
When user clicks next page
Then next [N] items are displayed
```

### Form Validation

```gherkin
# Required Field
Given user is on the form page
When user leaves [required field] empty
And clicks submit button
Then error message "[Field] is required" is displayed
And field is highlighted in red
And form is not submitted

# Format Validation
Given user is on the form page
When user enters invalid format in [field]
And clicks submit button
Then error message "[Expected format] is required" is displayed
And example of valid format is shown

# Real-time Validation
Given user is on the form page
When user finishes typing in [field] (on blur)
Then field is validated immediately
And error message appears if invalid
And success indicator appears if valid
```

### Notification System

```gherkin
# In-App Notification
Given a trigger event occurs
Then notification appears in the notification panel
And notification badge count increases
And notification contains relevant information and link

# Email Notification
Given a trigger event occurs
And user has email notifications enabled
Then email is sent within [N] minutes
And email contains relevant information
And email has working action links

# Push Notification (if applicable)
Given user has push notifications enabled
When trigger event occurs
Then push notification is delivered to user's device
And tapping notification opens relevant screen
```

---

## Quality Attributes

### Performance

```markdown
- [ ] Page loads in under [N] seconds on standard connection
- [ ] API response time is under [N]ms for 95th percentile
- [ ] No memory leaks during normal usage
- [ ] Handles [N] concurrent users without degradation
```

### Security

```markdown
- [ ] All user inputs are sanitized
- [ ] Authentication tokens expire after [N] hours/days
- [ ] Sensitive data is encrypted at rest and in transit
- [ ] Failed operations do not expose system details
- [ ] Rate limiting is enforced ([N] requests per [time])
```

### Accessibility

```markdown
- [ ] All interactive elements are keyboard accessible
- [ ] Screen reader compatibility verified
- [ ] Color contrast meets WCAG AA standards
- [ ] Error messages are announced to screen readers
- [ ] Focus management works correctly
```

### Responsiveness

```markdown
- [ ] Layout adapts correctly on mobile (< 768px)
- [ ] Layout adapts correctly on tablet (768px - 1024px)
- [ ] Layout adapts correctly on desktop (> 1024px)
- [ ] Touch targets are at least 44x44px on mobile
- [ ] No horizontal scrolling on any viewport
```

---

## Edge Cases to Consider

### Error Handling

```gherkin
# Network Error
Given user is performing an action
When network connection is lost
Then appropriate error message is displayed
And user's work is not lost
And retry option is available

# Server Error
Given server returns 500 error
Then user-friendly error message is displayed
And error is logged for debugging
And user can retry or contact support

# Timeout
Given request takes longer than [N] seconds
Then loading indicator is shown
And user can cancel the operation
And timeout error is shown after [N] seconds
```

### Boundary Conditions

```markdown
- [ ] Empty state: No items to display
- [ ] Single item: Only one item exists
- [ ] Maximum items: At capacity limit
- [ ] Long text: Text exceeds expected length
- [ ] Special characters: Input contains unicode/emoji
- [ ] Large numbers: Values at maximum range
```

### Concurrent Operations

```markdown
- [ ] Concurrent edits show appropriate conflict resolution
- [ ] Deleted items handled gracefully if accessed
- [ ] Session expiration handled mid-operation
- [ ] Race conditions prevented with proper locking
```

---

## Writing Tips

### Good AC Characteristics

✅ **SMART Criteria**
- **S**pecific: Clear and unambiguous
- **M**easurable: Can be objectively verified
- **A**chievable: Technically feasible
- **R**elevant: Aligned with user story
- **T**estable: Can write test cases from it

### Examples

```markdown
# ❌ Bad: Vague
- [ ] System should be fast
- [ ] User experience should be good

# ✅ Good: Specific & Measurable
- [ ] Page load time < 2 seconds on 3G connection
- [ ] User can complete checkout in < 3 clicks
```

### Common Mistakes to Avoid

```markdown
# ❌ Implementation details
- [ ] Use React hooks for state management

# ✅ Behavior focused
- [ ] State is preserved when user navigates away and returns

# ❌ Unclear scope
- [ ] Handle errors properly

# ✅ Clear scope
- [ ] Display error message when API returns 4xx/5xx
- [ ] Log error details to monitoring system
- [ ] Show retry button for transient errors
```

---

## Quick Reference

| Story Type | Minimum AC Count | Key Areas |
|------------|------------------|-----------|
| Simple CRUD | 4-6 | Create, Read, Update, Delete, Validation |
| User Flow | 5-8 | Happy path, Error states, Edge cases |
| Integration | 6-10 | Connection, Data sync, Error handling, Retry |
| Performance | 3-5 | Load time, Response time, Scalability |
