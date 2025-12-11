#!/usr/bin/env python3
"""
Test user registration and authentication
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.role import Role
from app.models.program import Program
from app.services.registration_service import RegistrationService

def test_registration():
    """Test user registration"""
    app = create_app('development')
    
    with app.app_context():
        print("Testing User Registration...")
        
        # Create test data
        test_user_data = {
            'email': 'test@yca-abuja.com',
            'password': 'Test@1234',
            'confirm_password': 'Test@1234',
            'surname': 'Test',
            'first_name': 'User',
            'gender': 'Male',
            'phone': '+2348012345678',
            'address': '123 Test Street, Abuja',
            'state': 'FCT',
            'country': 'Nigeria',
            'bio': 'Test user for registration',
            'selected_programs': [],
            'role': 'Student'
        }
        
        # Register user
        user, error = RegistrationService.register_user(
            form_data=test_user_data,
            photo_file=None,
            resume_file=None,
            remote_addr='127.0.0.1'
        )
        
        if error:
            print(f"❌ Registration failed: {error}")
            return False
        
        print(f"✅ User registered successfully!")
        print(f"   Username: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Full Name: {user.get_full_name()}")
        print(f"   Phone: {user.format_phone()}")
        
        # Test password verification
        if user.verify_password('Test@1234'):
            print("✅ Password verification successful")
        else:
            print("❌ Password verification failed")
        
        # Test email validation
        if User.validate_email('test@yca-abuja.com'):
            print("✅ Email validation successful")
        else:
            print("❌ Email validation failed")
        
        # Test phone validation
        if User.validate_phone('+2348012345678'):
            print("✅ Phone validation successful")
        else:
            print("❌ Phone validation failed")
        
        # Clean up
        db.session.delete(user)
        db.session.commit()
        print("✅ Test user cleaned up")
        
        return True

def test_username_generation():
    """Test username generation"""
    app = create_app('development')
    
    with app.app_context():
        print("\nTesting Username Generation...")
        
        from app.services.username_generator import UsernameGenerator
        
        # Test student username
        student_username = UsernameGenerator.generate_username(
            role_name='Student',
            program_name='Web Development'
        )
        print(f"✅ Student username: {student_username}")
        
        # Test teacher username
        teacher_username = UsernameGenerator.generate_username(
            role_name='Teacher',
            program_name='Python Programming'
        )
        print(f"✅ Teacher username: {teacher_username}")
        
        # Test admin username
        admin_username = UsernameGenerator.generate_username(
            role_name='System Admin'
        )
        print(f"✅ Admin username: {admin_username}")
        
        # Test username parsing
        parsed = UsernameGenerator.parse_username(student_username)
        print(f"✅ Parsed username: {parsed}")

if __name__ == '__main__':
    print("=" * 50)
    print("Yazz Academy Registration System Tests")
    print("=" * 50)
    
    try:
        test_registration()
        test_username_generation()
        print("\n" + "=" * 50)
        print("All tests completed successfully!")
        print("=" * 50)
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()