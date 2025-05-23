
# HTTP Methods: Comprehensive Technical Guide

## Introduction
HTTP methods define the actions to be performed on resources identified by URLs in an HTTP request. Each method has specific semantics regarding resource handling on the server.

## Core HTTP Methods

### GET
- **Purpose**: Retrieves data from a specified resource
- **Characteristics**:
  - Idempotent (multiple identical requests have same effect as single request)
  - Safe (read-only, doesn't change resource state)
  - Cacheable by default
- **Technical Implementation**:
  - Parameters passed in URL query string
  - Request body typically empty
  - Maximum URL length restrictions apply (~2048 characters in most browsers)
- **Status Codes**: 200 (OK), 304 (Not Modified), 404 (Not Found)

### POST
- **Purpose**: Submits data to be processed to a specified resource
- **Characteristics**:
  - Non-idempotent (multiple identical requests may produce different effects)
  - Unsafe (modifies server state)
  - Not cacheable by default unless specific cache controls are added
- **Technical Implementation**:
  - Parameters in request body
  - No URL length limitations for data
  - Supports various content types (application/json, application/x-www-form-urlencoded, multipart/form-data)
- **Status Codes**: 201 (Created), 200 (OK), 204 (No Content)

### PUT
- **Purpose**: Updates a resource or creates it if doesn't exist
- **Characteristics**:
  - Idempotent
  - Unsafe
  - Not cacheable
- **Technical Implementation**:
  - Complete resource representation in request body
  - Resource identifier specified in URL
  - Replaces entire resource
- **Status Codes**: 200 (OK), 201 (Created), 204 (No Content)

### DELETE
- **Purpose**: Removes specified resource
- **Characteristics**:
  - Idempotent
  - Unsafe
  - Not cacheable
- **Technical Implementation**:
  - Resource identifier in URL
  - May include authorization headers
  - Can include request body for complex delete operations
- **Status Codes**: 200 (OK), 202 (Accepted), 204 (No Content)

## Additional HTTP Methods

### HEAD
- **Purpose**: Identical to GET but returns only headers, no body
- **Use Cases**: Checking resource existence, metadata retrieval, cache validation
- **Technical Characteristics**: Safe, idempotent, cacheable

### OPTIONS
- **Purpose**: Describes communication options for target resource
- **Use Cases**: CORS preflight requests, API capability discovery
- **Technical Characteristics**: Safe, idempotent, not typically cached

### PATCH
- **Purpose**: Applies partial modifications to a resource
- **Technical Implementation**:
  - Contains only changed fields, not entire resource
  - Often uses JSON Patch (RFC 6902) or JSON Merge Patch (RFC 7396)
- **Characteristics**: Non-idempotent, unsafe

### TRACE
- **Purpose**: Performs message loop-back test along request path
- **Security**: Often disabled in production due to security concerns
- **Characteristics**: Safe, idempotent

### CONNECT
- **Purpose**: Establishes tunnel to server identified by target resource
- **Use Cases**: SSL tunneling for HTTPS through HTTP proxies
- **Technical Characteristics**: Not idempotent, unsafe

## HTTP Method Comparison Matrix

| Method  | Idempotent | Safe | Cacheable | Request Body | Response Body |
|---------|------------|------|-----------|--------------|---------------|
| GET     | Yes        | Yes  | Yes       | No           | Yes           |
| POST    | No         | No   | Rarely    | Yes          | Yes           |
| PUT     | Yes        | No   | No        | Yes          | Optional      |
| DELETE  | Yes        | No   | No        | Optional     | Optional      |
| HEAD    | Yes        | Yes  | Yes       | No           | No            |
| OPTIONS | Yes        | Yes  | No        | Optional     | Yes           |
| PATCH   | No         | No   | No        | Yes          | Optional      |
| TRACE   | Yes        | Yes  | No        | No           | Yes           |
| CONNECT | No         | No   | No        | No           | Yes           |

## Implementation Best Practices
- Use appropriate method for each operation based on semantics
- Implement proper status code responses
- Ensure idempotent operations remain truly idempotent
- Apply correct cache-control headers based on method type
- Follow RESTful principles for API design