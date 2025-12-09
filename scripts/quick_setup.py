#!/usr/bin/env python3
"""
Quick setup script for local development
"""

import sys
import os

# Add parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from app import create_app
from app.extensions import db
from seeders.roles_seeder import seed_roles
from seeders.programs_seeder import seed_programs
from app.models import User, Role
from app.extensions import bcrypt
from app.services.username_generator import UsernameGenerator
from datetime import datetime

def setup_database():
    """Set up the database with tables and seed data"""
    app = create_app('development')
    
    with app.app_context():
        print("=" * 60)
        print("YAZZ COMMUNICATION ACADEMY - LMS Setup")
        print("=" * 60)
        
        # Create tables
        print("\n📦 1. Creating database tables...")
        try:
            db.create_all()
            print("   ✅ Database tables created")
        except Exception as e:
            print(f"   ❌ Error creating tables: {e}")
            return
        
        # Seed roles and programs
        print("\n🌱 2. Seeding initial data...")
        try:
            seed_roles()
            print("   ✅ Roles seeded")
        except Exception as e:
            print(f"   ❌ Error seeding roles: {e}")
        
        try:
            seed_programs()
            print("   ✅ Programs seeded")
        except Exception as e:
            print(f"   ❌ Error seeding programs: {e}")
        
        # Create admin user
        print("\n👑 3. Creating admin user...")
        try:
            admin_role = Role.query.filter_by(name='System Admin').first()
            if admin_role:
                admin_email = 'admin@yca-abuja.com'
                existing_admin = User.query.filter_by(email=admin_email).first()
                
                if not existing_admin:
                    # Generate username
                    current_year = datetime.now().year % 100
                    username = UsernameGenerator.generate_username(
                        year=current_year,
                        role_name='System Admin'
                    )
                    
                    # Create admin
                    admin = User(
                        email=admin_email,
                        username=username,
                        first_name='System',
                        surname='Administrator',
                        gender='Male',
                        password_hash=bcrypt.generate_password_hash('Admin@123').decode('utf-8'),
                        is_active=True,
                        email_verified=True,
                        country='Nigeria',
                        phone='+2349079869903'
                    )
                    admin.roles.append(admin_role)
                    
                    db.session.add(admin)
                    db.session.commit()
                    
                    print(f"   ✅ Admin user created")
                    print(f"     📧 Email: {admin_email}")
                    print(f"     👤 Username: {username}")
                    print(f"     🔑 Password: Admin@123")
                else:
                    print("   ⚠️  Admin user already exists")
            else:
                print("   ❌ System Admin role not found")
        except Exception as e:
            print(f"   ❌ Error creating admin: {e}")
        
        # Show summary
        print("\n" + "=" * 60)
        print("SETUP COMPLETE!")
        print("=" * 60)
        
        # Count records
        roles_count = Role.query.count()
        programs_count = db.session.query(User.__table__.c.id).count()  # Fix for User.count()
        users_count = User.query.count()
        
        print(f"\n📊 Database Summary:")
        print(f"   • Roles: {roles_count}")
        print(f"   • Programs: {programs_count}")
        print(f"   • Users: {users_count}")
        
        print("\n🚀 To start the application:")
        print("   1. Activate virtual environment:")
        print("      Windows: venv\\Scripts\\activate")
        print("      Mac/Linux: source venv/bin/activate")
        print("   2. Start the server:")
        print("      python wsgi.py")
        print("   3. Open your browser:")
        print("      http://localhost:5000")
        print("   4. Login with:")
        print("      Email: admin@yca-abuja.com")
        print("      Password: Admin@123")
        print("\n🔧 Additional commands:")
        print("   flask list-programs     # List all programs")
        print("   flask list-roles        # List all roles")
        print("   flask test-username     # Test username generator")
        print("=" * 60)

if __name__ == '__main__':
    setup_database()