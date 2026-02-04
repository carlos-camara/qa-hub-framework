# 🌐 API Testing

The framework provides a robust set of Gherkin steps for testing RESTful APIs, built on top of the `requests` library with a focus on high-fidelity assertions and dynamic data.

## 📍 Environment Setup

Before sending requests, define the target environment and optional headers.

```gherkin
Given the API base URL is "https://api.example.com"
When I set request headers
  | Authorization | Bearer ${MY_TOKEN} |
  | Accept        | application/json   |
```

---

## 📤 Sending Requests

### Standard Methods
```gherkin
When I send a "GET" request to "/users"
When I send a "DELETE" request to "/users/123"
```

### Advanced Payloads
| Scenario | Example |
| :--- | :--- |
| **Query Params** | `When I send a "GET" request to "/search" with query parameters` |
| **JSON Body** | `When I send a "POST" request to "/orders" with JSON body` |
| **Form Data** | `When I send a "POST" request to "/upload" with form data` |
| **File Upload** | `When I upload the file "invoice.pdf" to "/api/v1/files"` |

---

## ✅ Core Assertions

### Value & Type Validation
The framework uses dot-notation to navigate complex JSON structures.

- `Then the response status code should be 200`
- `Then the response JSON path "user.id" should be 42`
- `Then the response JSON path "roles.0" should be "admin"`
- `Then the response JSON path "active" should be true`
- `Then the response JSON path "items" should be a "list"`

### Existence & Predicates
Verify structural integrity without checking specific values.

- `Then the response JSON path "optional_field" should exist`
- `Then the response JSON path "deprecated_field" should not exist`
- `Then the response JSON should be an object`
- `Then the response JSON should be an array`

---

## 📊 Collection Assertions

Validate the size of lists or dictionaries effectively.

- `Then the response JSON should have 10 elements`
- `Then the response JSON path "data.items" should have 5 elements`
- `Then the response JSON should not be empty`

---

## 🔢 Mathematical Comparisons

Perfect for validating ranges, timestamps, or price limits.

- `Then the response JSON path "price" should be > 10.0`
- `Then the response JSON path "stock" should be >= 1`
- `Then the response JSON path "discount" should be < 50`
- `Then the response time should be less than 500 ms`

---

## 🔄 Dynamic Variables

Capture values from one response and use them in subsequent requests using the `${var}` syntax.

```gherkin
Scenario: Create and Verify User
  When I send a "POST" request to "/users" with JSON body ...
  Then I store the response JSON path "id" as "NewUserId"
  And I send a "GET" request to "/users/${NewUserId}"
  Then the response status code should be 200
```

!!! tip "Token Resolution"
    You can use global tokens like `[UUID]` or `[NOW]` directly in your JSON bodies or URLs.
