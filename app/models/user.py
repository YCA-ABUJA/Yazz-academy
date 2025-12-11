from app.extensions import db, bcrypt
from datetime import datetime
import re
from sqlalchemy.dialects.mysql import JSON
import json

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
    linkedin_handle = db.Column(db.String(100))
    
    # Profile
    photo_path = db.Column(db.String(255))  # Path to uploaded photo
    resume_path = db.Column(db.String(255))  # Path to uploaded CV/Resume
    bio = db.Column(db.Text)  # Short bio (max 1000 chars)
    
    # Educational Background (stored as JSON)
    qualifications = db.Column(db.JSON, default=list)
    
    # Selected Programs/Courses (stored as JSON of program IDs)
    selected_programs = db.Column(db.JSON, default=list)
    
    # Authentication
    password_hash = db.Column(db.String(128), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    email_verified = db.Column(db.Boolean, default=False)
    email_verified_at = db.Column(db.DateTime)
    email_verification_token = db.Column(db.String(100))
    email_verification_sent_at = db.Column(db.DateTime)
    
    # 2FA
    two_factor_enabled = db.Column(db.Boolean, default=False)
    two_factor_secret = db.Column(db.String(32))
    two_factor_backup_codes = db.Column(db.JSON, default=list)
    
    # Login tracking
    last_login = db.Column(db.DateTime)
    last_login_ip = db.Column(db.String(45))
    login_count = db.Column(db.Integer, default=0)
    
    # Account status
    is_suspended = db.Column(db.Boolean, default=False)
    suspension_reason = db.Column(db.Text)
    suspended_until = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime)
    
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
        """Set password hash with validation"""
        if len(password) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        # Check password complexity
        if not any(char.isdigit() for char in password):
            raise ValueError('Password must contain at least one number')
        
        if not any(char.isupper() for char in password):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not any(char.islower() for char in password):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not any(char in '!@#$%^&*()_+-=[]{}|;:,.<>?' for char in password):
            raise ValueError('Password must contain at least one special character')
        
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
    
    @property
    def is_deleted(self):
        return self.deleted_at is not None
    
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
    
    def get_all_permissions(self):
        """Get all permissions for user across all roles"""
        all_permissions = {}
        for role in self.roles:
            permissions = role.permissions or {}
            for resource, actions in permissions.items():
                if resource not in all_permissions:
                    all_permissions[resource] = set()
                all_permissions[resource].update(actions)
        return all_permissions
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_regex, email) is not None
    
    @staticmethod
    def validate_phone(phone):
        """Validate phone number (E.164 format recommended)"""
        # Remove spaces, dashes, and parentheses
        cleaned_phone = re.sub(r'[\s\-\(\)]', '', phone)
        
        # Nigerian phone number validation
        if cleaned_phone.startswith('0'):
            cleaned_phone = '+234' + cleaned_phone[1:]
        
        # E.164 format validation
        phone_regex = r'^\+[1-9]\d{1,14}$'
        return re.match(phone_regex, cleaned_phone) is not None
    
    def format_phone(self):
        """Format phone number to E.164 format"""
        if not self.phone:
            return None
        
        cleaned_phone = re.sub(r'[\s\-\(\)]', '', self.phone)
        
        if cleaned_phone.startswith('0'):
            return '+234' + cleaned_phone[1:]
        elif cleaned_phone.startswith('234'):
            return '+' + cleaned_phone
        elif not cleaned_phone.startswith('+'):
            return '+' + cleaned_phone
        
        return cleaned_phone
    
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
    
    def to_dict(self):
        """Convert user to dictionary for API responses"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.get_full_name(),
            'display_name': self.display_name,
            'phone': self.format_phone(),
            'gender': self.gender,
            'roles': [role.name for role in self.roles],
            'is_active': self.is_active,
            'email_verified': self.email_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    def record_login(self, ip_address):
        """Record user login"""
        self.last_login = datetime.utcnow()
        self.last_login_ip = ip_address
        self.login_count = (self.login_count or 0) + 1
        db.session.commit()
    
    def generate_verification_token(self):
        """Generate email verification token"""
        import secrets
        self.email_verification_token = secrets.token_urlsafe(32)
        self.email_verification_sent_at = datetime.utcnow()
        db.session.commit()
        return self.email_verification_token
    
    def verify_email(self, token):
        """Verify email with token"""
        if (self.email_verification_token == token and 
            self.email_verification_sent_at and 
            (datetime.utcnow() - self.email_verification_sent_at).days < 7):
            
            self.email_verified = True
            self.email_verified_at = datetime.utcnow()
            self.email_verification_token = None
            db.session.commit()
            return True
        return False