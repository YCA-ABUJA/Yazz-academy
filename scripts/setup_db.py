#!/usr/bin/env python3
"""
Database setup script for Yazz Communication Academy LMS
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from seeders.roles_seeder import seed_roles
from seeders.programs_seeder import seed_programs

def setup_database():
    """Set up the database with tables and seed data"""
    app = create_app('development')
    
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("✓ Database tables created")
        
        print("\nSeeding initial data...")
        seed_roles()
        seed_programs()
        print("✓ Initial data seeded")
        
        print("\nDatabase setup complete!")

if __name__ == '__main__':
    setup_database()