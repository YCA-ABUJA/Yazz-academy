from app.extensions import db
from datetime import datetime
from app.models.user_roles import user_roles



class Role(db.Model):
    """Role model for RBAC"""
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    permissions = db.Column(db.JSON, default=dict)  # Store permissions as JSON
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = db.relationship('User', secondary=user_roles, back_populates='roles')
    
    def __repr__(self):
        return f'<Role {self.name}>'
    
    @staticmethod
    def get_default_permissions():
        """Return default permissions for each role"""
        return {
            'System Admin': {
                'users': ['create', 'read', 'update', 'delete', 'manage_roles'],
                'courses': ['create', 'read', 'update', 'delete', 'publish'],
                'financials': ['view', 'manage', 'export'],
                'settings': ['manage'],
                'reports': ['view', 'export'],
                'analytics': ['view'],
            },
            'Head of School': {
                'users': ['read', 'update'],
                'courses': ['create', 'read', 'update', 'publish'],
                'financials': ['view', 'export'],
                'settings': ['read'],
                'reports': ['view', 'export'],
                'analytics': ['view'],
            },
            'Teacher': {
                'courses': ['read', 'update_own'],
                'assignments': ['create', 'read', 'update', 'delete', 'grade'],
                'students': ['read_own'],
                'materials': ['upload', 'manage_own'],
            },
            'Student': {
                'courses': ['read_enrolled'],
                'assignments': ['read', 'submit'],
                'materials': ['read'],
                'profile': ['manage_own'],
            }
        }