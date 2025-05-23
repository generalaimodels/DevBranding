#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Validation Testing in Python
Demonstrating various validation techniques, patterns, and best practices
"""

import re
import json
import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union, Callable, Pattern, TypeVar, Generic
from enum import Enum


# =====================================================================
# Core Validation Framework
# =====================================================================

class ValidationError(Exception):
    """Custom exception for validation errors"""
    
    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict] = None):
        self.message = message
        self.field = field
        self.details = details or {}
        super().__init__(self.message)


class ValidationResult:
    """Represents the result of a validation operation"""
    
    def __init__(self, is_valid: bool, errors: Optional[List[ValidationError]] = None):
        self.is_valid = is_valid
        self.errors = errors or []
    
    def add_error(self, error: ValidationError) -> None:
        """Add a validation error to the result"""
        self.is_valid = False
        self.errors.append(error)
    
    def __bool__(self) -> bool:
        """Allow direct boolean evaluation of validation result"""
        return self.is_valid
    
    def __str__(self) -> str:
        if self.is_valid:
            return "Validation passed"
        return f"Validation failed: {', '.join(str(e) for e in self.errors)}"


T = TypeVar('T')


class Validator(Generic[T], ABC):
    """Abstract base class for validators"""
    
    @abstractmethod
    def validate(self, value: T) -> ValidationResult:
        """Validate the given value and return a ValidationResult"""
        pass
    
    def __call__(self, value: T) -> ValidationResult:
        """Make validators callable"""
        return self.validate(value)


# =====================================================================
# Basic Data Type Validators
# =====================================================================

class StringValidator(Validator[str]):
    """Validates string values"""
    
    def __init__(self, min_length: int = 0, max_length: Optional[int] = None, 
                 pattern: Optional[Union[str, Pattern]] = None, 
                 allowed_values: Optional[List[str]] = None):
        self.min_length = min_length
        self.max_length = max_length
        self.pattern = re.compile(pattern) if isinstance(pattern, str) else pattern
        self.allowed_values = allowed_values
    
    def validate(self, value: Any) -> ValidationResult:
        result = ValidationResult(True)
        
        # Type validation
        if not isinstance(value, str):
            result.add_error(ValidationError(
                f"Expected string but got {type(value).__name__}"))
            return result
        
        # Length validation
        if len(value) < self.min_length:
            result.add_error(ValidationError(
                f"String length must be at least {self.min_length} characters"))
        
        if self.max_length is not None and len(value) > self.max_length:
            result.add_error(ValidationError(
                f"String length must not exceed {self.max_length} characters"))
        
        # Pattern validation
        if self.pattern and not self.pattern.match(value):
            result.add_error(ValidationError(
                f"String does not match required pattern {self.pattern.pattern}"))
        
        # Allowed values validation
        if self.allowed_values and value not in self.allowed_values:
            result.add_error(ValidationError(
                f"Value must be one of: {', '.join(self.allowed_values)}"))
        
        return result


class NumberValidator(Validator[Union[int, float]]):
    """Validates numeric values"""
    
    def __init__(self, min_value: Optional[Union[int, float]] = None, 
                max_value: Optional[Union[int, float]] = None,
                integer_only: bool = False,
                allow_negative: bool = True,
                allow_zero: bool = True):
        self.min_value = min_value
        self.max_value = max_value
        self.integer_only = integer_only
        self.allow_negative = allow_negative
        self.allow_zero = allow_zero
    
    def validate(self, value: Any) -> ValidationResult:
        result = ValidationResult(True)
        
        # Type validation
        if self.integer_only and not isinstance(value, int):
            result.add_error(ValidationError(
                f"Expected integer but got {type(value).__name__}"))
            return result
        
        if not isinstance(value, (int, float)):
            result.add_error(ValidationError(
                f"Expected number but got {type(value).__name__}"))
            return result
        
        # Range validation
        if self.min_value is not None and value < self.min_value:
            result.add_error(ValidationError(
                f"Value must be at least {self.min_value}"))
        
        if self.max_value is not None and value > self.max_value:
            result.add_error(ValidationError(
                f"Value must not exceed {self.max_value}"))
        
        # Sign validation
        if not self.allow_negative and value < 0:
            result.add_error(ValidationError("Negative values are not allowed"))
        
        if not self.allow_zero and value == 0:
            result.add_error(ValidationError("Zero value is not allowed"))
        
        return result


class BooleanValidator(Validator[bool]):
    """Validates boolean values"""
    
    def validate(self, value: Any) -> ValidationResult:
        result = ValidationResult(True)
        
        if not isinstance(value, bool):
            result.add_error(ValidationError(
                f"Expected boolean but got {type(value).__name__}"))
        
        return result


class DateValidator(Validator[datetime.date]):
    """Validates date values"""
    
    def __init__(self, min_date: Optional[datetime.date] = None,
                max_date: Optional[datetime.date] = None,
                format_str: Optional[str] = None):
        self.min_date = min_date
        self.max_date = max_date
        self.format_str = format_str
    
    def validate(self, value: Any) -> ValidationResult:
        result = ValidationResult(True)
        
        # Parse string to date if format is provided
        if isinstance(value, str) and self.format_str:
            try:
                value = datetime.datetime.strptime(value, self.format_str).date()
            except ValueError:
                result.add_error(ValidationError(
                    f"Date string does not match format {self.format_str}"))
                return result
        
        # Type validation
        if not isinstance(value, datetime.date):
            result.add_error(ValidationError(
                f"Expected date but got {type(value).__name__}"))
            return result
        
        # Range validation
        if self.min_date and value < self.min_date:
            result.add_error(ValidationError(
                f"Date must be on or after {self.min_date}"))
        
        if self.max_date and value > self.max_date:
            result.add_error(ValidationError(
                f"Date must be on or before {self.max_date}"))
        
        return result


# =====================================================================
# Composite Validators
# =====================================================================

class ListValidator(Validator[List[Any]]):
    """Validates list values and their items"""
    
    def __init__(self, item_validator: Optional[Validator] = None,
                min_length: int = 0, max_length: Optional[int] = None,
                unique_items: bool = False):
        self.item_validator = item_validator
        self.min_length = min_length
        self.max_length = max_length
        self.unique_items = unique_items
    
    def validate(self, value: Any) -> ValidationResult:
        result = ValidationResult(True)
        
        # Type validation
        if not isinstance(value, list):
            result.add_error(ValidationError(
                f"Expected list but got {type(value).__name__}"))
            return result
        
        # Length validation
        if len(value) < self.min_length:
            result.add_error(ValidationError(
                f"List must contain at least {self.min_length} items"))
        
        if self.max_length is not None and len(value) > self.max_length:
            result.add_error(ValidationError(
                f"List must not contain more than {self.max_length} items"))
        
        # Uniqueness validation
        if self.unique_items and len(value) != len(set(map(str, value))):
            result.add_error(ValidationError("List items must be unique"))
        
        # Item validation
        if self.item_validator:
            for i, item in enumerate(value):
                item_result = self.item_validator.validate(item)
                if not item_result.is_valid:
                    for error in item_result.errors:
                        error.field = f"[{i}]" + (f".{error.field}" if error.field else "")
                        result.add_error(error)
        
        return result


class DictValidator(Validator[Dict[str, Any]]):
    """Validates dictionary values and their fields"""
    
    def __init__(self, schema: Optional[Dict[str, Validator]] = None,
                required_fields: Optional[List[str]] = None,
                allow_unknown: bool = False):
        self.schema = schema or {}
        self.required_fields = required_fields or []
        self.allow_unknown = allow_unknown
    
    def validate(self, value: Any) -> ValidationResult:
        result = ValidationResult(True)
        
        # Type validation
        if not isinstance(value, dict):
            result.add_error(ValidationError(
                f"Expected dictionary but got {type(value).__name__}"))
            return result
        
        # Required fields validation
        missing_fields = [field for field in self.required_fields if field not in value]
        if missing_fields:
            result.add_error(ValidationError(
                f"Missing required fields: {', '.join(missing_fields)}"))
        
        # Unknown fields validation
        if not self.allow_unknown:
            unknown_fields = [field for field in value if field not in self.schema]
            if unknown_fields:
                result.add_error(ValidationError(
                    f"Unknown fields: {', '.join(unknown_fields)}"))
        
        # Field validation
        for field, validator in self.schema.items():
            if field in value:
                field_result = validator.validate(value[field])
                if not field_result.is_valid:
                    for error in field_result.errors:
                        error.field = f"{field}" + (f".{error.field}" if error.field else "")
                        result.add_error(error)
        
        return result


class UnionValidator(Validator[Any]):
    """Validates a value against multiple validators, passing if any one passes"""
    
    def __init__(self, validators: List[Validator]):
        self.validators = validators
    
    def validate(self, value: Any) -> ValidationResult:
        if not self.validators:
            return ValidationResult(True)
        
        all_errors = []
        for validator in self.validators:
            result = validator.validate(value)
            if result.is_valid:
                return result
            all_errors.extend(result.errors)
        
        result = ValidationResult(False)
        result.add_error(ValidationError(
            "Value did not match any of the expected types", 
            details={"errors": [e.message for e in all_errors]}))
        return result


class OptionalValidator(Validator[Any]):
    """Validates a value that can be None or match another validator"""
    
    def __init__(self, validator: Validator):
        self.validator = validator
    
    def validate(self, value: Any) -> ValidationResult:
        if value is None:
            return ValidationResult(True)
        return self.validator.validate(value)


# =====================================================================
# Common Validation Patterns
# =====================================================================

class EmailValidator(StringValidator):
    """Validates email addresses"""
    
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    def __init__(self, allow_empty: bool = False):
        super().__init__(
            min_length=0 if allow_empty else 1,
            pattern=self.EMAIL_PATTERN
        )
    
    def validate(self, value: Any) -> ValidationResult:
        result = super().validate(value)
        
        # Additional email-specific validation
        if result.is_valid and value:
            # Check for double dots
            if '..' in value:
                result.add_error(ValidationError("Email cannot contain consecutive dots"))
            
            # Check domain has at least one dot
            parts = value.split('@')
            if len(parts) == 2 and '.' not in parts[1]:
                result.add_error(ValidationError("Email domain must contain at least one dot"))
        
        return result


class PasswordValidator(StringValidator):
    """Validates password strength"""
    
    def __init__(self, min_length: int = 8, require_uppercase: bool = True,
                require_lowercase: bool = True, require_digit: bool = True,
                require_special: bool = True):
        super().__init__(min_length=min_length)
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digit = require_digit
        self.require_special = require_special
    
    def validate(self, value: Any) -> ValidationResult:
        result = super().validate(value)
        
        if not isinstance(value, str):
            return result
        
        # Check for required character classes
        if self.require_uppercase and not any(c.isupper() for c in value):
            result.add_error(ValidationError(
                "Password must contain at least one uppercase letter"))
        
        if self.require_lowercase and not any(c.islower() for c in value):
            result.add_error(ValidationError(
                "Password must contain at least one lowercase letter"))
        
        if self.require_digit and not any(c.isdigit() for c in value):
            result.add_error(ValidationError(
                "Password must contain at least one digit"))
        
        if self.require_special and not any(not c.isalnum() for c in value):
            result.add_error(ValidationError(
                "Password must contain at least one special character"))
        
        return result


class PhoneNumberValidator(Validator[str]):
    """Validates phone numbers in various formats"""
    
    def __init__(self, allow_international: bool = True, 
                country_code: Optional[str] = None):
        self.allow_international = allow_international
        self.country_code = country_code
        
        # Basic pattern for digits, spaces, dashes, and parentheses
        self.basic_pattern = re.compile(r'^[\d\s\(\)\-\+\.]+$')
        
        # E.164 international format (+NNNNNNNNNNN)
        self.e164_pattern = re.compile(r'^\+\d{1,3}\d{6,14}$')
    
    def validate(self, value: Any) -> ValidationResult:
        result = ValidationResult(True)
        
        if not isinstance(value, str):
            result.add_error(ValidationError(
                f"Expected string but got {type(value).__name__}"))
            return result
        
        # Remove whitespace for checking
        clean_value = ''.join(value.split())
        
        # Basic character validation
        if not self.basic_pattern.match(value):
            result.add_error(ValidationError(
                "Phone number contains invalid characters"))
            return result
        
        # Check digit count (excluding formatting characters)
        digits = ''.join(c for c in clean_value if c.isdigit())
        if len(digits) < 7 or len(digits) > 15:
            result.add_error(ValidationError(
                "Phone number must contain between 7 and 15 digits"))
        
        # International format validation
        if clean_value.startswith('+'):
            if not self.allow_international:
                result.add_error(ValidationError(
                    "International phone numbers are not allowed"))
            elif not self.e164_pattern.match(clean_value):
                result.add_error(ValidationError(
                    "International phone number must be in E.164 format"))
            elif self.country_code and not clean_value.startswith(f"+{self.country_code}"):
                result.add_error(ValidationError(
                    f"Phone number must start with country code +{self.country_code}"))
        
        return result


class URLValidator(StringValidator):
    """Validates URLs"""
    
    URL_PATTERN = re.compile(
        r'^(https?:\/\/)'  # Protocol (http:// or https://)
        r'(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)'  # Subdomain
        r'*([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])'  # Domain name
        r'\.[a-zA-Z]{2,}'  # TLD
        r'(\:[0-9]+)?'  # Port (optional)
        r'(\/[-a-zA-Z0-9_%\.~#?&=]*)*'  # Path and query (optional)
        r'$'
    )
    
    def __init__(self, require_https: bool = False, allowed_domains: Optional[List[str]] = None):
        super().__init__(pattern=self.URL_PATTERN)
        self.require_https = require_https
        self.allowed_domains = allowed_domains
    
    def validate(self, value: Any) -> ValidationResult:
        result = super().validate(value)
        
        if not isinstance(value, str) or not result.is_valid:
            return result
        
        # Protocol validation
        if self.require_https and not value.startswith('https://'):
            result.add_error(ValidationError("URL must use HTTPS protocol"))
        
        # Domain validation
        if self.allowed_domains:
            domain = value.split('://', 1)[1].split('/', 1)[0].split(':', 1)[0]
            allowed = False
            for allowed_domain in self.allowed_domains:
                if domain == allowed_domain or domain.endswith(f".{allowed_domain}"):
                    allowed = True
                    break
            
            if not allowed:
                result.add_error(ValidationError(
                    f"URL domain must be one of: {', '.join(self.allowed_domains)}"))
        
        return result


# =====================================================================
# Custom Validation Rules
# =====================================================================

class CustomValidator(Validator[Any]):
    """Allows for custom validation logic via callable"""
    
    def __init__(self, validation_func: Callable[[Any], Union[bool, str]],
                error_message: str = "Validation failed"):
        self.validation_func = validation_func
        self.error_message = error_message
    
    def validate(self, value: Any) -> ValidationResult:
        result = ValidationResult(True)
        
        validation_result = self.validation_func(value)
        
        if isinstance(validation_result, bool):
            if not validation_result:
                result.add_error(ValidationError(self.error_message))
        elif isinstance(validation_result, str):
            if validation_result:  # Non-empty string means error
                result.add_error(ValidationError(validation_result))
        
        return result


# =====================================================================
# Decorator-based Validation
# =====================================================================

def validate_arguments(**validators):
    """Decorator for validating function arguments"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Get function signature
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # Validate arguments
            validation_errors = []
            for param_name, validator in validators.items():
                if param_name in bound_args.arguments:
                    result = validator.validate(bound_args.arguments[param_name])
                    if not result.is_valid:
                        for error in result.errors:
                            error.field = param_name + (f".{error.field}" if error.field else "")
                            validation_errors.append(error)
            
            # Raise exception if validation fails
            if validation_errors:
                raise ValidationError(
                    f"Invalid arguments for {func.__name__}",
                    details={"errors": [e.message for e in validation_errors]}
                )
            
            # Call function with validated arguments
            return func(*args, **kwargs)
        return wrapper
    return decorator


# =====================================================================
# Schema Validation with JSON
# =====================================================================

class JSONSchemaValidator(Validator[Dict[str, Any]]):
    """Validates JSON data against a schema"""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
        self._build_validator_from_schema()
    
    def _build_validator_from_schema(self):
        """Constructs a DictValidator from a JSON schema"""
        schema_validators = {}
        required_fields = []
        
        for field_name, field_schema in self.schema.get("properties", {}).items():
            field_type = field_schema.get("type")
            
            if field_name in self.schema.get("required", []):
                required_fields.append(field_name)
            
            # Build validator based on field type
            if field_type == "string":
                validator = StringValidator(
                    min_length=field_schema.get("minLength", 0),
                    max_length=field_schema.get("maxLength"),
                    pattern=field_schema.get("pattern"),
                    allowed_values=field_schema.get("enum")
                )
            elif field_type == "number" or field_type == "integer":
                validator = NumberValidator(
                    min_value=field_schema.get("minimum"),
                    max_value=field_schema.get("maximum"),
                    integer_only=(field_type == "integer")
                )
            elif field_type == "boolean":
                validator = BooleanValidator()
            elif field_type == "array":
                items_schema = field_schema.get("items", {})
                item_validator = self._create_validator_for_schema(items_schema)
                validator = ListValidator(
                    item_validator=item_validator,
                    min_length=field_schema.get("minItems", 0),
                    max_length=field_schema.get("maxItems"),
                    unique_items=field_schema.get("uniqueItems", False)
                )
            elif field_type == "object":
                nested_schema = {
                    "properties": field_schema.get("properties", {}),
                    "required": field_schema.get("required", [])
                }
                nested_validator = JSONSchemaValidator(nested_schema)
                validator = nested_validator
            else:
                # Default to allowing any value
                validator = Validator()
            
            schema_validators[field_name] = validator
        
        self.dict_validator = DictValidator(
            schema=schema_validators,
            required_fields=required_fields,
            allow_unknown=not self.schema.get("additionalProperties", True)
        )
    
    def _create_validator_for_schema(self, schema: Dict[str, Any]) -> Validator:
        """Creates a validator for a schema section"""
        field_type = schema.get("type")
        
        if field_type == "string":
            return StringValidator(
                min_length=schema.get("minLength", 0),
                max_length=schema.get("maxLength"),
                pattern=schema.get("pattern"),
                allowed_values=schema.get("enum")
            )
        elif field_type == "number" or field_type == "integer":
            return NumberValidator(
                min_value=schema.get("minimum"),
                max_value=schema.get("maximum"),
                integer_only=(field_type == "integer")
            )
        elif field_type == "boolean":
            return BooleanValidator()
        elif field_type == "array":
            items_schema = schema.get("items", {})
            item_validator = self._create_validator_for_schema(items_schema)
            return ListValidator(
                item_validator=item_validator,
                min_length=schema.get("minItems", 0),
                max_length=schema.get("maxItems"),
                unique_items=schema.get("uniqueItems", False)
            )
        elif field_type == "object":
            nested_schema = {
                "properties": schema.get("properties", {}),
                "required": schema.get("required", [])
            }
            return JSONSchemaValidator(nested_schema)
        else:
            # Default to allowing any value
            return Validator()
    
    def validate(self, value: Any) -> ValidationResult:
        """Validate value against JSON schema"""
        return self.dict_validator.validate(value)


# =====================================================================
# Domain Models with Built-in Validation
# =====================================================================

@dataclass
class ValidatedModel:
    """Base class for models with built-in validation"""
    
    def validate(self) -> ValidationResult:
        """Validate the model using field validators"""
        result = ValidationResult(True)
        
        for field_name, field_value in self.__dict__.items():
            validator_name = f"_{field_name}_validator"
            validator = getattr(self.__class__, validator_name, None)
            
            if validator and isinstance(validator, Validator):
                field_result = validator.validate(field_value)
                if not field_result.is_valid:
                    for error in field_result.errors:
                        error.field = field_name + (f".{error.field}" if error.field else "")
                        result.add_error(error)
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ValidatedModel':
        """Create an instance from a dictionary and validate it"""
        instance = cls(**data)
        result = instance.validate()
        if not result.is_valid:
            raise ValidationError(
                f"Invalid {cls.__name__}",
                details={"errors": [e.message for e in result.errors]}
            )
        return instance


# =====================================================================
# Example Usage Classes
# =====================================================================

class UserStatus(Enum):
    """User account status"""
    ACTIVE = "active"
    PENDING = "pending"
    SUSPENDED = "suspended"
    INACTIVE = "inactive"


class User(ValidatedModel):
    """User model with validation"""
    
    def __init__(self, id: Optional[int] = None, 
                username: str = "", 
                email: str = "",
                password: str = "",
                age: Optional[int] = None,
                status: str = "pending",
                created_at: Optional[datetime.datetime] = None):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.age = age
        self.status = status
        self.created_at = created_at or datetime.datetime.now()
    
    # Field validators
    _id_validator = OptionalValidator(NumberValidator(min_value=1, integer_only=True))
    _username_validator = StringValidator(min_length=3, max_length=50, 
                                         pattern=r'^[a-zA-Z0-9_-]+$')
    _email_validator = EmailValidator()
    _password_validator = PasswordValidator()
    _age_validator = OptionalValidator(NumberValidator(min_value=13, max_value=120, integer_only=True))
    _status_validator = StringValidator(allowed_values=[s.value for s in UserStatus])
    _created_at_validator = DateValidator()


# =====================================================================
# Complete Example: Form Validation
# =====================================================================

def validate_registration_form(form_data: Dict[str, Any]) -> ValidationResult:
    """Validate a user registration form"""
    schema = {
        "properties": {
            "username": {
                "type": "string",
                "minLength": 3,
                "maxLength": 50,
                "pattern": "^[a-zA-Z0-9_-]+$"
            },
            "email": {
                "type": "string",
                "format": "email"
            },
            "password": {
                "type": "string",
                "minLength": 8
            },
            "confirm_password": {
                "type": "string"
            },
            "age": {
                "type": "integer",
                "minimum": 13
            },
            "terms_accepted": {
                "type": "boolean"
            },
            "profile": {
                "type": "object",
                "properties": {
                    "first_name": {"type": "string"},
                    "last_name": {"type": "string"},
                    "bio": {"type": "string", "maxLength": 500}
                }
            }
        },
        "required": ["username", "email", "password", "confirm_password", "terms_accepted"]
    }
    
    # Use JSON schema validator for basic validation
    validator = JSONSchemaValidator(schema)
    result = validator.validate(form_data)
    
    # Custom validation rules
    if result.is_valid:
        # Check password confirmation
        if form_data.get("password") != form_data.get("confirm_password"):
            result.add_error(ValidationError(
                "Passwords do not match", field="confirm_password"))
        
        # Check password strength with more detailed rules
        password = form_data.get("password", "")
        password_validator = PasswordValidator()
        password_result = password_validator.validate(password)
        if not password_result.is_valid:
            for error in password_result.errors:
                error.field = "password"
                result.add_error(error)
        
        # Check terms acceptance
        if not form_data.get("terms_accepted", False):
            result.add_error(ValidationError(
                "You must accept the terms and conditions", field="terms_accepted"))
    
    return result


# =====================================================================
# Testing and Demonstration
# =====================================================================

def demonstration():
    """Demonstrate validation functionality"""
    
    # Basic string validation
    email_validator = EmailValidator()
    email_result = email_validator.validate("user@example.com")
    assert email_result.is_valid
    
    invalid_email_result = email_validator.validate("invalid-email")
    assert not invalid_email_result.is_valid
    
    # Number validation
    age_validator = NumberValidator(min_value=0, max_value=120, integer_only=True)
    age_result = age_validator.validate(25)
    assert age_result.is_valid
    
    invalid_age_result = age_validator.validate(150)
    assert not invalid_age_result.is_valid
    
    # List validation
    tags_validator = ListValidator(
        item_validator=StringValidator(min_length=1, max_length=20),
        min_length=1,
        max_length=5,
        unique_items=True
    )
    valid_tags = ["python", "validation", "testing"]
    assert tags_validator.validate(valid_tags).is_valid
    
    invalid_tags = ["python", "python", "too-long-tag-that-exceeds-limit"]
    assert not tags_validator.validate(invalid_tags).is_valid
    
    # Dictionary/schema validation
    person_validator = DictValidator(
        schema={
            "name": StringValidator(min_length=1),
            "age": NumberValidator(min_value=0, integer_only=True),
            "email": EmailValidator()
        },
        required_fields=["name", "email"]
    )
    
    valid_person = {
        "name": "John Doe",
        "age": 30,
        "email": "john@example.com"
    }
    assert person_validator.validate(valid_person).is_valid
    
    invalid_person = {
        "name": "",
        "age": "thirty",
        "email": "invalid-email"
    }
    invalid_result = person_validator.validate(invalid_person)
    assert not invalid_result.is_valid
    assert len(invalid_result.errors) == 3
    
    # Model validation
    user = User(
        username="john_doe",
        email="john@example.com",
        password="SecureP@ss123",
        age=25,
        status="active"
    )
    user_result = user.validate()
    assert user_result.is_valid
    
    invalid_user = User(
        username="j",  # Too short
        email="invalid-email",
        password="weak",  # Too weak
        age=10,  # Too young
        status="unknown"  # Invalid status
    )
    invalid_user_result = invalid_user.validate()
    assert not invalid_user_result.is_valid
    assert len(invalid_user_result.errors) == 5
    
    # Form validation example
    valid_form = {
        "username": "john_doe",
        "email": "john@example.com",
        "password": "SecureP@ss123",
        "confirm_password": "SecureP@ss123",
        "age": 25,
        "terms_accepted": True,
        "profile": {
            "first_name": "John",
            "last_name": "Doe",
            "bio": "Software developer"
        }
    }
    form_result = validate_registration_form(valid_form)
    assert form_result.is_valid
    
    invalid_form = {
        "username": "jd",  # Too short
        "email": "invalid-email",
        "password": "pass123",
        "confirm_password": "different_password",  # Doesn't match
        "age": 10,  # Too young
        "terms_accepted": False,  # Must be true
    }
    invalid_form_result = validate_registration_form(invalid_form)
    assert not invalid_form_result.is_valid
    
    print("All validation tests passed successfully.")


if __name__ == "__main__":
    demonstration()