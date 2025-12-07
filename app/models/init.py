# Import all models for Flask-Migrate to detect
from .user import User
from .role import Role
from .registration_sequence import RegistrationSequence
from .program import Program

__all__ = ['User', 'Role', 'RegistrationSequence', 'Program']