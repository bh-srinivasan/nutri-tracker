"""
Security utilities for input validation and sanitization
"""
import re
from markupsafe import escape
from typing import Optional, Dict, Any

class InputValidator:
    """Utility class for input validation and sanitization"""
    
    @staticmethod
    def sanitize_string(text: Optional[str]) -> str:
        """
        Sanitize string input to prevent XSS attacks
        
        Args:
            text: Input string to sanitize
            
        Returns:
            Sanitized string
        """
        if not text:
            return ""
        
        # Remove potentially dangerous characters and escape HTML
        sanitized = escape(str(text).strip())
        return sanitized
    
    @staticmethod
    def validate_username(username: str) -> tuple[bool, str]:
        """
        Validate username format and requirements
        
        Args:
            username: Username to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not username:
            return False, "Username is required"
        
        username = username.strip()
        
        if len(username) < 3:
            return False, "Username must be at least 3 characters long"
        
        if len(username) > 50:
            return False, "Username must be less than 50 characters"
        
        # Allow alphanumeric, underscore, and hyphen
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            return False, "Username can only contain letters, numbers, underscores, and hyphens"
        
        return True, ""
    
    @staticmethod
    def validate_email(email: Optional[str]) -> tuple[bool, str]:
        """
        Validate email format (optional field)
        
        Args:
            email: Email to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not email or email.strip() == "":
            return True, ""  # Email is optional
        
        email = email.strip().lower()
        
        # Basic email regex validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, email):
            return False, "Please enter a valid email address"
        
        if len(email) > 254:  # RFC 5321 limit
            return False, "Email address is too long"
        
        return True, ""
    
    @staticmethod
    def validate_name(name: str, field_name: str = "Name") -> tuple[bool, str]:
        """
        Validate first/last name fields
        
        Args:
            name: Name to validate
            field_name: Name of the field for error messages
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not name:
            return False, f"{field_name} is required"
        
        name = name.strip()
        
        if len(name) < 1:
            return False, f"{field_name} is required"
        
        if len(name) > 50:
            return False, f"{field_name} must be less than 50 characters"
        
        # Allow letters, spaces, hyphens, and apostrophes
        if not re.match(r"^[a-zA-Z\s\-']+$", name):
            return False, f"{field_name} can only contain letters, spaces, hyphens, and apostrophes"
        
        return True, ""
    
    @staticmethod
    def validate_password(password: str) -> tuple[bool, str]:
        """
        Validate password strength requirements
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not password:
            return False, "Password is required"
        
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if len(password) > 128:
            return False, "Password is too long"
        
        # Check for required character types
        has_upper = bool(re.search(r'[A-Z]', password))
        has_lower = bool(re.search(r'[a-z]', password))
        has_digit = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
        
        missing_requirements = []
        if not has_upper:
            missing_requirements.append("uppercase letter")
        if not has_lower:
            missing_requirements.append("lowercase letter")
        if not has_digit:
            missing_requirements.append("number")
        if not has_special:
            missing_requirements.append("special character")
        
        if missing_requirements:
            return False, f"Password must contain at least one: {', '.join(missing_requirements)}"
        
        return True, ""
    
    @staticmethod
    def sanitize_user_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize user input data dictionary
        
        Args:
            data: Dictionary of user data
            
        Returns:
            Sanitized data dictionary
        """
        sanitized = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                sanitized[key] = InputValidator.sanitize_string(value)
            elif isinstance(value, bool):
                sanitized[key] = bool(value)
            elif isinstance(value, (int, float)):
                sanitized[key] = value
            else:
                # Convert other types to string and sanitize
                sanitized[key] = InputValidator.sanitize_string(str(value))
        
        return sanitized

class FormValidator:
    """Enhanced form validation for admin operations"""
    
    @staticmethod
    def validate_edit_user_form(form_data: Dict[str, Any]) -> tuple[bool, Dict[str, str]]:
        """
        Validate edit user form data
        
        Args:
            form_data: Form data dictionary
            
        Returns:
            Tuple of (is_valid, errors_dict)
        """
        errors = {}
        
        # Sanitize input data
        clean_data = InputValidator.sanitize_user_data(form_data)
        
        # Validate username
        username = clean_data.get('username', '')
        is_valid, error = InputValidator.validate_username(username)
        if not is_valid:
            errors['username'] = error
        
        # Validate email (optional)
        email = clean_data.get('email', '')
        is_valid, error = InputValidator.validate_email(email)
        if not is_valid:
            errors['email'] = error
        
        # Validate first name
        first_name = clean_data.get('first_name', '')
        is_valid, error = InputValidator.validate_name(first_name, "First name")
        if not is_valid:
            errors['first_name'] = error
        
        # Validate last name
        last_name = clean_data.get('last_name', '')
        is_valid, error = InputValidator.validate_name(last_name, "Last name")
        if not is_valid:
            errors['last_name'] = error
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_password_reset_form(form_data: Dict[str, Any]) -> tuple[bool, Dict[str, str]]:
        """
        Validate password reset form data
        
        Args:
            form_data: Form data dictionary
            
        Returns:
            Tuple of (is_valid, errors_dict)
        """
        errors = {}
        
        # Validate new password
        new_password = form_data.get('new_password', '')
        is_valid, error = InputValidator.validate_password(new_password)
        if not is_valid:
            errors['new_password'] = error
        
        return len(errors) == 0, errors
