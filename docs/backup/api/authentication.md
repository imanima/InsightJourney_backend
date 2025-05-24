# Authentication

## Register
```http
POST /auth/register
```
```json
{
    "email": "user@example.com",
    "password": "password123",
    "name": "User Name"
}
```

## Login
```http
POST /auth/login
```
```json
{
    "email": "user@example.com",
    "password": "password123"
}
```
Response:
```json
{
    "token": "jwt_token",
    "id": "user_id",
    "email": "user@example.com",
    "name": "User Name"
}
```

## Usage
Include token in all requests:
```http
Authorization: Bearer <token>
```

## Token Format

### Access Token

```json
{
    "typ": "JWT",
    "alg": "HS256"
}
{
    "sub": "user_id",
    "iat": 1234567890,
    "exp": 1234567890,
    "type": "access"
}
```

### Refresh Token

```json
{
    "typ": "JWT",
    "alg": "HS256"
}
{
    "sub": "user_id",
    "iat": 1234567890,
    "exp": 1234567890,
    "type": "refresh"
}
```

## Error Responses

1. **Invalid Token**
```json
{
    "status": "error",
    "message": "Invalid token",
    "code": "INVALID_TOKEN"
}
```

2. **Expired Token**
```json
{
    "status": "error",
    "message": "Token has expired",
    "code": "TOKEN_EXPIRED"
}
```

3. **Missing Token**
```json
{
    "status": "error",
    "message": "Authorization header is required",
    "code": "MISSING_TOKEN"
}
```

## Security Considerations

### Token Storage

1. **Frontend**
   - Store access token in memory
   - Store refresh token in secure HTTP-only cookie
   - Never store tokens in localStorage

2. **Token Expiration**
   - Access tokens: 1 hour
   - Refresh tokens: 24 hours

### Password Requirements

- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character

### Rate Limiting

- Login: 5 attempts per minute
- Register: 3 attempts per minute
- Refresh: 10 attempts per minute

## Example Implementation

### JavaScript/TypeScript
```typescript
class AuthService {
    private baseUrl = 'http://localhost:5000/api/v1';
    private accessToken: string | null = null;

    async login(email: string, password: string) {
        const response = await fetch(`${this.baseUrl}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();
        if (data.status === 'success') {
            this.accessToken = data.data.access_token;
        }
        return data;
    }

    async makeAuthenticatedRequest(endpoint: string, options = {}) {
        if (!this.accessToken) {
            throw new Error('Not authenticated');
        }

        const response = await fetch(`${this.baseUrl}${endpoint}`, {
            ...options,
            headers: {
                ...options.headers,
                'Authorization': `Bearer ${this.accessToken}`
            }
        });

        return response.json();
    }
}
```

### Python
```python
import requests

class AuthService:
    def __init__(self):
        self.base_url = 'http://localhost:5000/api/v1'
        self.access_token = None

    def login(self, email: str, password: str) -> dict:
        response = requests.post(
            f'{self.base_url}/auth/login',
            json={'email': email, 'password': password}
        )
        data = response.json()
        if data['status'] == 'success':
            self.access_token = data['data']['access_token']
        return data

    def make_authenticated_request(self, endpoint: str, **kwargs) -> dict:
        if not self.access_token:
            raise Exception('Not authenticated')

        headers = kwargs.pop('headers', {})
        headers['Authorization'] = f'Bearer {self.access_token}'

        response = requests.request(
            kwargs.pop('method', 'GET'),
            f'{self.base_url}{endpoint}',
            headers=headers,
            **kwargs
        )
        return response.json()
``` 