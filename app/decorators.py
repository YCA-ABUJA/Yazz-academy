from functools import wraps
from flask import abort, current_app
from flask_login import current_user

def role_required(role_name):
    """Decorator to require specific role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return current_app.login_manager.unauthorized()
            
            if not current_user.has_role(role_name):
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """Decorator for admin users"""
    return role_required('System Admin')(f)

def teacher_required(f):
    """Decorator for teacher users"""
    return role_required('Teacher')(f)

def student_required(f):
    """Decorator for student users"""
    return role_required('Student')(f)

def permission_required(resource, action):
    """Decorator to require specific permission"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return current_app.login_manager.unauthorized()
            
            if not current_user.has_permission(resource, action):
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator