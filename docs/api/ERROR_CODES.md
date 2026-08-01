# Standardized API Error Codes Reference

## Error Code Catalog

| Error Code | HTTP Status | Description | Action Required |
|---|---|---|---|
| `VALIDATION_ERROR` | 422 | Request payload or path parameter validation failed. | Fix input parameters according to schema. |
| `BUSINESS_RULE_VIOLATION` | 400 / 422 | Domain business rule invariant violated. | Ensure requested ticker or action is valid. |
| `UNAUTHENTICATED` | 401 | Missing or invalid authentication token/API key. | Provide valid HTTP Bearer token or API key. |
| `UNAUTHORIZED` | 403 | Insufficient permission roles to access resource. | Request required role permissions. |
| `NOT_FOUND` | 404 | Target resource, ticker, or endpoint not found. | Verify target URL or resource ID. |
| `PROVIDER_ERROR` | 502 / 504 | Upstream market data provider connection or response failure. | Retry with exponential backoff. |
| `INTERNAL_SERVER_ERROR` | 500 | Unhandled internal exception occurred. | Contact backend engineering support. |
