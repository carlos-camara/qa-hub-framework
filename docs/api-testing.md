# 🌐 API Testing

The framework provides a robust set of Gherkin steps for testing RESTful APIs. These steps handle the heavy lifting of HTTP requests, variable management, and complex JSON assertions.

## 📍 Basic Setup

Before sending requests, you must define the target environment:

```gherkin
Given the API base URL is "https://api.example.com"
```

## 📤 Sending Requests

### Simple Requests
Standard HTTP methods are supported:
```gherkin
When I send a "GET" request to "/users"
When I send a "DELETE" request to "/users/123"
```

### Query Parameters
Use a Behave table to send parameters:
```gherkin
When I send a "GET" request to "/search" with query parameters
  | q      | status |
  | search | active |
```

### JSON Payloads
Use a docstring to define the body:
```gherkin
When I send a "POST" request to "/orders" with JSON body
  """
  {
    "product_id": 1,
    "quantity": 2
  }
  """
```

## ✅ Assertions

The framework uses dot-notation to navigate JSON responses easily.

| Step | Example |
|------|---------|
| **Status Code** | `Then the response status code should be 200` |
| **JSON String** | `Then the response JSON path "user.name" should be "John"` |
| **JSON Integer** | `Then the response JSON path "id" should be 42` |
| **Regex Match** | `Then the response JSON path "uuid" should match regex "^[0-9a-f-]{36}$"` |
| **Type Check** | `Then the response JSON path "items" should be a "list"` |
| **Null Check** | `Then the response JSON path "deleted_at" should be null` |

## 🔄 Variables & Orchestration

You can capture values from one response and use them in subsequent requests within the same scenario.

1. **Store a value**:
   ```gherkin
   Then I store the response JSON path "token" as "auth_token"
   ```
2. **Use the value**:
   ```gherkin
   When I send a "GET" request to "/profile/${auth_token}"
   ```

## 🐞 Debugging Tools

Use these steps to inspect the traffic during development:
- `Then I print the response JSON`: Outputs the pretty-printed JSON body.
- `Then I print the request headers`: Outputs exactly what was sent to the server.
