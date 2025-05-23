#!/usr/bin/env python3
"""
HTTP Methods Implementation in Python
A comprehensive implementation showcasing all HTTP methods with proper handling,
authentication, error management, and best practices.
"""

import json
import logging
import os
import time
from typing import Dict, Any, Optional, Union, List, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import hashlib
import hmac
import base64
from urllib.parse import urlencode

# Third-party imports
import requests
from flask import Flask, request, jsonify, Response, make_response, g
from flask_cors import CORS
from werkzeug.http import HTTP_STATUS_CODES


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HttpStatusCode(Enum):
    """HTTP Status Codes with descriptions"""
    # 2xx Success
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204
    
    # 3xx Redirection
    MOVED_PERMANENTLY = 301
    FOUND = 302
    NOT_MODIFIED = 304
    
    # 4xx Client Errors
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    CONFLICT = 409
    GONE = 410
    
    # 5xx Server Errors
    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503


@dataclass
class Resource:
    """Data model for resources manipulated via HTTP methods"""
    id: int
    name: str
    description: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert resource to dictionary"""
        return asdict(self)
    
    def update(self, data: Dict[str, Any]) -> None:
        """Update resource with partial data (PATCH operation)"""
        for key, value in data.items():
            if hasattr(self, key) and key != 'id':
                setattr(self, key, value)
        self.updated_at = time.time()
    
    def replace(self, data: Dict[str, Any]) -> None:
        """Replace resource with complete data (PUT operation)"""
        self.name = data.get('name', '')
        self.description = data.get('description')
        self.metadata = data.get('metadata', {})
        self.updated_at = time.time()


class ResourceStore:
    """In-memory storage for resources to demonstrate HTTP operations"""
    def __init__(self):
        self.resources: Dict[int, Resource] = {}
        self.next_id: int = 1
    
    def get_all(self) -> List[Resource]:
        """GET all resources"""
        return list(self.resources.values())
    
    def get(self, resource_id: int) -> Optional[Resource]:
        """GET a specific resource by ID"""
        return self.resources.get(resource_id)
    
    def create(self, data: Dict[str, Any]) -> Resource:
        """POST a new resource"""
        resource = Resource(
            id=self.next_id,
            name=data.get('name', ''),
            description=data.get('description'),
            metadata=data.get('metadata', {})
        )
        self.resources[resource.id] = resource
        self.next_id += 1
        return resource
    
    def update(self, resource_id: int, data: Dict[str, Any]) -> Optional[Resource]:
        """PUT to update a resource completely"""
        resource = self.get(resource_id)
        if resource:
            resource.replace(data)
            return resource
        return None
    
    def patch(self, resource_id: int, data: Dict[str, Any]) -> Optional[Resource]:
        """PATCH to update a resource partially"""
        resource = self.get(resource_id)
        if resource:
            resource.update(data)
            return resource
        return None
    
    def delete(self, resource_id: int) -> bool:
        """DELETE a resource"""
        if resource_id in self.resources:
            del self.resources[resource_id]
            return True
        return False


class AuthManager:
    """Authentication and authorization manager"""
    def __init__(self):
        # In a real app, these would be securely stored
        self._api_keys = {"test_api_key": "admin"}
        self._jwt_secret = "super_secret_key"  # Would use env var in production
    
    def validate_api_key(self, api_key: str) -> bool:
        """Validate an API key"""
        return api_key in self._api_keys
    
    def get_role_for_key(self, api_key: str) -> Optional[str]:
        """Get role associated with an API key"""
        return self._api_keys.get(api_key)
    
    def generate_hmac_signature(self, data: str, secret: str) -> str:
        """Generate HMAC signature for request signing"""
        signature = hmac.new(
            secret.encode(),
            data.encode(),
            hashlib.sha256
        ).digest()
        return base64.b64encode(signature).decode()
    
    def verify_hmac_signature(self, data: str, signature: str, secret: str) -> bool:
        """Verify HMAC signature"""
        expected = self.generate_hmac_signature(data, secret)
        return hmac.compare_digest(expected, signature)


class CacheControl:
    """Handles HTTP caching mechanisms"""
    
    @staticmethod
    def generate_etag(content: Union[str, Dict, bytes]) -> str:
        """Generate ETag for content"""
        if isinstance(content, dict):
            content = json.dumps(content, sort_keys=True)
        if isinstance(content, str):
            content = content.encode('utf-8')
        return hashlib.md5(content).hexdigest()
    
    @staticmethod
    def add_cache_headers(
        response: Response, 
        etag: Optional[str] = None,
        max_age: int = 0,
        must_revalidate: bool = True
    ) -> Response:
        """Add cache control headers to response"""
        if etag:
            response.headers['ETag'] = etag
        
        cache_directives = []
        if max_age > 0:
            cache_directives.append(f"max-age={max_age}")
        if must_revalidate:
            cache_directives.append("must-revalidate")
        
        response.headers['Cache-Control'] = ", ".join(cache_directives)
        return response


# Initialize Flask application
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize our components
resource_store = ResourceStore()
auth_manager = AuthManager()

# Add some sample data
resource_store.create({"name": "Sample Resource 1", "description": "A sample resource"})
resource_store.create({"name": "Sample Resource 2", "description": "Another sample resource"})


@app.before_request
def authenticate():
    """Authenticate requests before processing"""
    # Skip authentication for OPTIONS (CORS preflight)
    if request.method == 'OPTIONS':
        return None
    
    # Check for API key in header
    api_key = request.headers.get('X-API-Key')
    if not api_key or not auth_manager.validate_api_key(api_key):
        return jsonify({"error": "Invalid or missing API key"}), HttpStatusCode.UNAUTHORIZED.value
    
    # Store authentication info for the route handler
    g.role = auth_manager.get_role_for_key(api_key)
    return None


# GET implementation
@app.route('/api/resources', methods=['GET'])
def get_resources():
    """Implementation of GET method to retrieve all resources"""
    resources = [r.to_dict() for r in resource_store.get_all()]
    
    # Generate ETag for caching
    etag = CacheControl.generate_etag(resources)
    if request.headers.get('If-None-Match') == etag:
        return '', HttpStatusCode.NOT_MODIFIED.value
    
    response = make_response(jsonify(resources))
    # Add cache headers (cacheable for 60 seconds)
    return CacheControl.add_cache_headers(response, etag=etag, max_age=60)


@app.route('/api/resources/<int:resource_id>', methods=['GET'])
def get_resource(resource_id):
    """Implementation of GET method to retrieve a specific resource"""
    resource = resource_store.get(resource_id)
    if not resource:
        return jsonify({"error": "Resource not found"}), HttpStatusCode.NOT_FOUND.value
    
    resource_dict = resource.to_dict()
    etag = CacheControl.generate_etag(resource_dict)
    
    # If client provided ETag and it matches, return 304 Not Modified
    if request.headers.get('If-None-Match') == etag:
        return '', HttpStatusCode.NOT_MODIFIED.value
    
    response = make_response(jsonify(resource_dict))
    return CacheControl.add_cache_headers(response, etag=etag, max_age=60)


# HEAD implementation
@app.route('/api/resources/<int:resource_id>', methods=['HEAD'])
def head_resource(resource_id):
    """
    Implementation of HEAD method
    Returns same headers as GET but no body, useful for checking if resource exists
    """
    resource = resource_store.get(resource_id)
    if not resource:
        return '', HttpStatusCode.NOT_FOUND.value
    
    resource_dict = resource.to_dict()
    etag = CacheControl.generate_etag(resource_dict)
    
    response = make_response('')  # Empty body for HEAD
    response.headers['Content-Type'] = 'application/json'
    response.headers['Content-Length'] = str(len(json.dumps(resource_dict)))
    return CacheControl.add_cache_headers(response, etag=etag, max_age=60)


# POST implementation
@app.route('/api/resources', methods=['POST'])
def create_resource():
    """Implementation of POST method to create a new resource"""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), HttpStatusCode.BAD_REQUEST.value
    
    try:
        data = request.get_json()
        if not data.get('name'):
            return jsonify({"error": "Name is required"}), HttpStatusCode.BAD_REQUEST.value
        
        new_resource = resource_store.create(data)
        return jsonify(new_resource.to_dict()), HttpStatusCode.CREATED.value
    except Exception as e:
        logger.error(f"Error creating resource: {str(e)}")
        return jsonify({"error": str(e)}), HttpStatusCode.INTERNAL_SERVER_ERROR.value


# PUT implementation
@app.route('/api/resources/<int:resource_id>', methods=['PUT'])
def update_resource(resource_id):
    """Implementation of PUT method to update or create a specific resource"""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), HttpStatusCode.BAD_REQUEST.value
    
    try:
        data = request.get_json()
        if not data.get('name'):
            return jsonify({"error": "Name is required"}), HttpStatusCode.BAD_REQUEST.value
        
        resource = resource_store.get(resource_id)
        status_code = HttpStatusCode.OK.value
        
        # If resource doesn't exist, create it (PUT is idempotent)
        if not resource:
            # In a RESTful API, the client specifies the ID in the URL
            # For this example, we'll create a new resource with the specified ID
            resource = Resource(
                id=resource_id,
                name=data.get('name', ''),
                description=data.get('description'),
                metadata=data.get('metadata', {})
            )
            resource_store.resources[resource_id] = resource
            status_code = HttpStatusCode.CREATED.value
        else:
            # Replace the existing resource entirely
            resource.replace(data)
        
        return jsonify(resource.to_dict()), status_code
    except Exception as e:
        logger.error(f"Error updating resource: {str(e)}")
        return jsonify({"error": str(e)}), HttpStatusCode.INTERNAL_SERVER_ERROR.value


# PATCH implementation
@app.route('/api/resources/<int:resource_id>', methods=['PATCH'])
def patch_resource(resource_id):
    """Implementation of PATCH method to partially update a resource"""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), HttpStatusCode.BAD_REQUEST.value
    
    try:
        data = request.get_json()
        updated_resource = resource_store.patch(resource_id, data)
        
        if not updated_resource:
            return jsonify({"error": "Resource not found"}), HttpStatusCode.NOT_FOUND.value
        
        return jsonify(updated_resource.to_dict())
    except Exception as e:
        logger.error(f"Error patching resource: {str(e)}")
        return jsonify({"error": str(e)}), HttpStatusCode.INTERNAL_SERVER_ERROR.value


# DELETE implementation
@app.route('/api/resources/<int:resource_id>', methods=['DELETE'])
def delete_resource(resource_id):
    """Implementation of DELETE method to remove a resource"""
    if resource_store.delete(resource_id):
        # Return 204 No Content for successful DELETE
        return '', HttpStatusCode.NO_CONTENT.value
    else:
        # If resource doesn't exist, still return success (DELETE is idempotent)
        return '', HttpStatusCode.NO_CONTENT.value


# OPTIONS implementation
@app.route('/api/resources', methods=['OPTIONS'])
@app.route('/api/resources/<int:resource_id>', methods=['OPTIONS'])
def options_resource(resource_id=None):
    """
    Implementation of OPTIONS method
    Returns available HTTP methods and CORS headers
    """
    response = make_response('')
    if resource_id is None:
        # Collection endpoint allows different methods than individual resource
        response.headers['Allow'] = 'GET, POST, OPTIONS'
    else:
        response.headers['Allow'] = 'GET, PUT, PATCH, DELETE, HEAD, OPTIONS'
    
    # Add CORS headers
    response.headers['Access-Control-Allow-Methods'] = response.headers['Allow']
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, X-API-Key'
    return response


# TRACE implementation (typically disabled in production)
@app.route('/api/trace', methods=['TRACE'])
def trace_request():
    """
    Implementation of TRACE method
    Returns the request headers back to the client for debugging
    """
    # In production, this would usually be disabled for security
    headers_dict = {key: value for key, value in request.headers.items()}
    return jsonify({
        "method": request.method,
        "url": request.url,
        "headers": headers_dict
    })


# CONNECT implementation
@app.route('/api/connect', methods=['CONNECT'])
def connect_tunnel():
    """
    Mock implementation of CONNECT method
    In real scenarios, this would establish a tunnel to another server
    """
    # This is just a demonstration - real CONNECT would establish a TCP tunnel
    return jsonify({
        "message": "CONNECT method demonstration - would establish a tunnel in real implementation"
    }), HttpStatusCode.OK.value


# Client implementation to demonstrate HTTP methods
class HttpClient:
    """A client to demonstrate HTTP method calls"""
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.headers = {
            'Content-Type': 'application/json',
            'X-API-Key': api_key
        }
        self.session = requests.Session()
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> requests.Response:
        """Perform GET request"""
        url = f"{self.base_url}/{endpoint}"
        return self.session.get(url, headers=self.headers, params=params)
    
    def head(self, endpoint: str) -> requests.Response:
        """Perform HEAD request"""
        url = f"{self.base_url}/{endpoint}"
        return self.session.head(url, headers=self.headers)
    
    def post(self, endpoint: str, data: Dict) -> requests.Response:
        """Perform POST request"""
        url = f"{self.base_url}/{endpoint}"
        return self.session.post(url, headers=self.headers, json=data)
    
    def put(self, endpoint: str, data: Dict) -> requests.Response:
        """Perform PUT request"""
        url = f"{self.base_url}/{endpoint}"
        return self.session.put(url, headers=self.headers, json=data)
    
    def patch(self, endpoint: str, data: Dict) -> requests.Response:
        """Perform PATCH request"""
        url = f"{self.base_url}/{endpoint}"
        return self.session.patch(url, headers=self.headers, json=data)
    
    def delete(self, endpoint: str) -> requests.Response:
        """Perform DELETE request"""
        url = f"{self.base_url}/{endpoint}"
        return self.session.delete(url, headers=self.headers)
    
    def options(self, endpoint: str) -> requests.Response:
        """Perform OPTIONS request"""
        url = f"{self.base_url}/{endpoint}"
        return self.session.options(url, headers=self.headers)
    
    def trace(self, endpoint: str) -> requests.Response:
        """Perform TRACE request"""
        url = f"{self.base_url}/{endpoint}"
        return self.session.request("TRACE", url, headers=self.headers)
    
    def connect(self, endpoint: str) -> requests.Response:
        """Perform CONNECT request"""
        url = f"{self.base_url}/{endpoint}"
        return self.session.request("CONNECT", url, headers=self.headers)


# Example usage function
def demonstrate_http_methods():
    """Function to demonstrate all HTTP methods using the client"""
    client = HttpClient("http://localhost:5000/api", "test_api_key")
    
    # GET all resources
    response = client.get("resources")
    print(f"GET all resources: {response.status_code}")
    print(response.json())
    
    # GET single resource
    response = client.get("resources/1")
    print(f"GET single resource: {response.status_code}")
    print(response.json())
    
    # HEAD request
    response = client.head("resources/1")
    print(f"HEAD request: {response.status_code}")
    print(f"Headers: {response.headers}")
    
    # POST request
    new_resource = {
        "name": "New Resource",
        "description": "Created via POST",
        "metadata": {"key": "value"}
    }
    response = client.post("resources", new_resource)
    print(f"POST request: {response.status_code}")
    print(response.json())
    
    # PUT request
    update_data = {
        "name": "Updated Resource",
        "description": "Updated via PUT",
        "metadata": {"updated": True}
    }
    response = client.put("resources/1", update_data)
    print(f"PUT request: {response.status_code}")
    print(response.json())
    
    # PATCH request
    patch_data = {
        "description": "Partially updated via PATCH"
    }
    response = client.patch("resources/1", patch_data)
    print(f"PATCH request: {response.status_code}")
    print(response.json())
    
    # DELETE request
    response = client.delete("resources/2")
    print(f"DELETE request: {response.status_code}")
    
    # OPTIONS request
    response = client.options("resources")
    print(f"OPTIONS request: {response.status_code}")
    print(f"Allowed methods: {response.headers.get('Allow')}")
    
    # TRACE request
    response = client.trace("trace")
    print(f"TRACE request: {response.status_code}")
    print(response.json())
    
    # CONNECT request
    response = client.connect("connect")
    print(f"CONNECT request: {response.status_code}")
    print(response.json())


if __name__ == "__main__":
    # Run the Flask server in a separate process in a real scenario
    # For demonstration, you'd run this file and then call the demonstrate_http_methods()
    # function from another script
    app.run(debug=True, port=5000)
    
    # In a real scenario, you'd call this after the server is running
    demonstrate_http_methods()