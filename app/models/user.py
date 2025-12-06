from app.extensions import db, bcrypt
from datetime import datetime
import re

class User(db.Model):
    """User model for all roles"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Personal Information
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20))
    
    # Name fields
    surname = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100))
    gender = db.Column(db.Enum('Male', 'Female', 'Other'), nullable=False)
    
    # Contact Information
    address = db.Column(db.Text)
    state = db.Column(db.String(100))
    country = db.Column(db.String(100), default='Nigeria')
    
    # Social Media
    facebook_handle = db.Column(db.String(100))
    twitter_handle = db.Column(db.String(100))
    github_handle = db.Column(db.String(100))
    
    # Profile
    photo_path = db.Column(db.String(255))  # Path to uploaded photo
    resume_path = db.Column(db.String(255))  # Path to uploaded CV/Resume
    bio = db.Column(db.Text)  # Short bio (max 1000 chars)
    
    # Educational Background (stored as JSON)
    qualifications = db.Column(db.JSON, default=list)
    
    # Authentication
    password_hash = db.Column(db.String(128), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    email_verified = db.Column(db.Boolean, default=False)
    email_verified_at = db.Column(db.DateTime)
    
    # 2FA
    two_factor_enabled = db.Column(db.Boolean, default=False)
    two_factor_secret = db.Column(db.String(32))
    
    # Timestamps
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    roles = db.relationship('Role', secondary='user_roles', back_populates='users')
    
    # Methods
    def __repr__(self):
        return f'<User {self.username} - {self.email}>'
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        """Set password hash"""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def verify_password(self, password):
        """Verify password against hash"""
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def get_id(self):
        """Required by Flask-Login"""
        return str(self.id)
    
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    def has_role(self, role_name):
        """Check if user has a specific role"""
        return any(role.name == role_name for role in self.roles)
    
    def has_permission(self, resource, action):
        """Check if user has permission for resource:action"""
        for role in self.roles:
            permissions = role.permissions or {}
            if resource in permissions and action in permissions[resource]:
                return True
        return False
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_regex, email) is not None
    
    @staticmethod
    def validate_phone(phone):
        """Validate phone number (E.164 format recommended)"""
        # Basic validation - can be enhanced
        phone_regex = r'^\+?[1-9]\d{1,14}$'
        return re.match(phone_regex, phone) is not None
    
    def get_full_name(self):
        """Get user's full name"""
        if self.middle_name:
            return f"{self.surname} {self.first_name} {self.middle_name}"
        return f"{self.surname} {self.first_name}"
    
    @property
    def display_name(self):
        """Get display name (First Name + Last Initial)"""
        if self.first_name and self.surname:
            return f"{self.first_name} {self.surname[0]}."
        return self.username