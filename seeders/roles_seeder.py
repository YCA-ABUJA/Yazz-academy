from app.extensions import db
from app.models.role import Role

def seed_roles():
    """Seed initial roles with permissions"""
    roles_data = [
        {
            'name': 'System Admin',
            'description': 'Full system access and management',
            'permissions': Role.get_default_permissions()['System Admin']
        },
        {
            'name': 'Head of School',
            'description': 'Head of the academy',
            'permissions': Role.get_default_permissions()['Head of School']
        },
        {
            'name': 'Secretary',
            'description': 'Administrative secretary',
            'permissions': {
                'users': ['read', 'update'],
                'courses': ['read'],
                'settings': ['read']
            }
        },
        {
            'name': 'Registrar',
            'description': 'Handles student registrations and records',
            'permissions': {
                'users': ['create', 'read', 'update'],
                'courses': ['read'],
                'enrollments': ['create', 'read', 'update', 'delete']
            }
        },
        {
            'name': 'Financial Secretary',
            'description': 'Handles financial transactions and reporting',
            'permissions': {
                'users': ['read'],
                'courses': ['read'],
                'financials': ['view', 'manage', 'export'],
                'payments': ['view', 'process', 'refund']
            }
        },
        {
            'name': 'Logistic Manager',
            'description': 'Manages logistics and resources',
            'permissions': {
                'resources': ['manage'],
                'scheduling': ['manage'],
                'settings': ['read']
            }
        },
        {
            'name': 'Teacher',
            'description': 'Course instructor',
            'permissions': Role.get_default_permissions()['Teacher']
        },
        {
            'name': 'Student',
            'description': 'Registered student',
            'permissions': Role.get_default_permissions()['Student']
        },
        {
            'name': 'Guest',
            'description': 'Guest user with limited access',
            'permissions': {
                'courses': ['read'],
                'blog': ['read']
            }
        }
    ]
    
    for role_data in roles_data:
        role = Role.query.filter_by(name=role_data['name']).first()
        if not role:
            role = Role(
                name=role_data['name'],
                description=role_data['description'],
                permissions=role_data.get('permissions', {})
            )
            db.session.add(role)
    
    db.session.commit()
    print(f"✓ Seeded {len(roles_data)} roles")