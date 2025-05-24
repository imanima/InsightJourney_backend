# Frontend Authentication Guide for Insight Journey API

This guide provides sample code for frontend developers to integrate with the Insight Journey authentication API.

## Base URL

```
https://insight-journey-a47jf6g6sa-uc.a.run.app/api/v1
```

## 1. User Registration

### Endpoint

```
POST /auth/register
```

### Request Format

```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "name": "User Name"
}
```

### Sample Code (JavaScript/Fetch)

```javascript
async function registerUser(email, password, name) {
  const response = await fetch('https://insight-journey-a47jf6g6sa-uc.a.run.app/api/v1/auth/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      email: email,
      password: password,
      name: name
    })
  });
  
  const data = await response.json();
  return data;
}
```

### Sample Response

```json
{
  "email": "user@example.com",
  "name": "User Name",
  "id": "U_77896259-9daf-43a4-a04c-f0249debb0cb",
  "is_admin": false,
  "created_at": "2025-05-14T23:23:37.376954",
  "disabled": false
}
```

## 2. User Login

### Endpoint

```
POST /auth/login
```

### Important Note

The login endpoint uses `username` as the parameter name but it expects an email address. This is due to the OAuth2 password flow standard that the backend implements.

### Request Format (form-urlencoded)

```
username=user@example.com&password=SecurePassword123!
```

### Sample Code (JavaScript/Fetch)

```javascript
// Login with email and password (form-urlencoded format)
// UPDATED - Ensure correct error handling
async function loginUser(email, password) {
  // Create URLSearchParams object for form data
  const formData = new URLSearchParams();
  formData.append('username', email);  // Note: parameter name is 'username' but we pass the email
  formData.append('password', password);
  
  const response = await fetch('https://insight-journey-a47jf6g6sa-uc.a.run.app/api/v1/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: formData
  });
  
  if (!response.ok) {
    // Handle error responses
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Login failed');
  }
  
  const data = await response.json();
  
  // Store the token in a secure way (memory, HttpOnly cookie in production)
  // For demo/development, localStorage might be used, but it's not recommended for production
  localStorage.setItem('auth_token', data.access_token);
  
  return data;
}
```javascript
async function loginUser(email, password) {
  // Create form data
  const formData = new URLSearchParams();
  formData.append('username', email);  // Note: parameter name is 'username' but it's the email
  formData.append('password', password);
  
  const response = await fetch('https://insight-journey-a47jf6g6sa-uc.a.run.app/api/v1/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: formData
  });
  
  const data = await response.json();
  
  // Save the token for authenticated requests
  if (data.access_token) {
    localStorage.setItem('auth_token', data.access_token);
  }
  
  return data;
}
```

### Sample Response

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## 3. Get Current User

### Endpoint

```
GET /auth/me
```

### Headers

```
Authorization: Bearer <access_token>
```

### Sample Code (JavaScript/Fetch)

```javascript
async function getCurrentUser() {
  // Get the token from storage
  const token = localStorage.getItem('auth_token');
  
  if (!token) {
    throw new Error('Authentication required');
  }
  
  const response = await fetch('https://insight-journey-a47jf6g6sa-uc.a.run.app/api/v1/auth/me', {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return await response.json();
}
```

### Sample Response

```json
{
  "id": "U_77896259-9daf-43a4-a04c-f0249debb0cb",
  "email": "user@example.com",
  "name": "User Name",
  "is_admin": false,
  "created_at": "2025-05-14T23:23:37.376954",
  "disabled": false
}
```

## 4. Update User Credentials

### Endpoint

```
PUT /auth/credentials
```

### Request Format

```json
{
  "current_password": "OldPassword123!",
  "new_password": "NewPassword456!"
}
```

### Sample Code (JavaScript/Fetch)

```javascript
async function updatePassword(currentPassword, newPassword) {
  const token = localStorage.getItem('auth_token');
  
  if (!token) {
    throw new Error('Authentication required');
  }
  
  const response = await fetch('https://insight-journey-a47jf6g6sa-uc.a.run.app/api/v1/auth/credentials', {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      current_password: currentPassword,
      new_password: newPassword
    })
  });
  
  return await response.json();
}
```

### Sample Response

```json
{
  "success": true,
  "message": "Password updated successfully"
}
```

## 5. Error Handling

### Common HTTP Status Codes

- **200 OK**: Request successful
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid input (validation error)
- **401 Unauthorized**: Authentication required or invalid token
- **403 Forbidden**: Not enough permissions
- **422 Unprocessable Entity**: Input validation failed
- **500 Internal Server Error**: Server-side error

### Sample Error Response

```json
{
  "detail": "Invalid credentials"
}
```

Or for validation errors:

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "password"],
      "msg": "String should have at least 8 characters",
      "input": "pass",
      "ctx": {"min_length": 8}
    }
  ]
}
```

## 6. Token Storage Best Practices

1. **Do not store tokens in localStorage** for production environments due to XSS vulnerability risks
2. Instead, use:
   - **HttpOnly cookies** (if your backend supports it)
   - **In-memory storage** with a refresh token mechanism
3. Implement automatic token refresh when tokens expire
4. Add logout functionality that clears tokens

## 7. Security Considerations

1. **HTTPS only**: All requests must use HTTPS
2. **Input validation**: Validate user inputs before sending to API
3. **Error handling**: Handle errors gracefully without exposing sensitive information
4. **Logout**: Implement a reliable logout mechanism
5. **Session timeout**: Notify users about session expiration

## React Sample Implementation

```jsx
import { useState } from 'react';

function LoginForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      // Create form data
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);
      
      const response = await fetch('https://insight-journey-a47jf6g6sa-uc.a.run.app/api/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: formData
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Login failed');
      }
      
      // Save token and redirect
      localStorage.setItem('auth_token', data.access_token);
      window.location.href = '/dashboard';
      
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Login</h2>
      
      {error && <div className="error">{error}</div>}
      
      <div>
        <label htmlFor="email">Email:</label>
        <input
          type="email"
          id="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
      </div>
      
      <div>
        <label htmlFor="password">Password:</label>
        <input
          type="password"
          id="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
      </div>
      
      <button type="submit" disabled={loading}>
        {loading ? 'Logging in...' : 'Login'}
      </button>
    </form>
  );
}

export default LoginForm;
``` 