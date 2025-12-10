#!/usr/bin/env python3
"""
Quick setup script for Yazz Academy LMS
"""
import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def setup_project():
    """Set up the project structure and database"""
    
    print("Setting up Yazz Academy LMS...")
    
    # Create necessary directories
    directories = [
        'app/static/css',
        'app/static/js',
        'app/static/images',
        'app/templates/auth',
        'app/templates/marketing',
        'app/templates/admin',
        'app/templates/teacher',
        'app/templates/student',
        'uploads/photos',
        'uploads/resumes',
        'uploads/course_materials',
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")
    
    # Copy .env.example if .env doesn't exist
    if not os.path.exists('.env') and os.path.exists('.env.example'):
        with open('.env.example', 'r') as src, open('.env', 'w') as dst:
            dst.write(src.read())
        print("✓ Created .env file from .env.example")
    
    print("\nSetup complete!")
    print("\nNext steps:")
    print("1. Edit .env file with your database credentials")
    print("2. Run: python scripts/setup_db.py")
    print("3. Run: flask create-admin")
    print("4. Run: python run.py")

if __name__ == '__main__':
    setup_project()