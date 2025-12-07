from flask import Flask
from config import config
from .extensions import init_extensions, db
import os

def create_app(config_name='default'):
    """Application factory"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Ensure upload folder exists
    upload_folder = app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
        os.makedirs(os.path.join(upload_folder, 'photos'))
        os.makedirs(os.path.join(upload_folder, 'resumes'))
        os.makedirs(os.path.join(upload_folder, 'course_materials'))
    
    # Initialize extensions
    init_extensions(app)
    
    # Import models AFTER extensions are initialized
    with app.app_context():
        # Import models for Flask-Migrate to detect
        from .models.user import User
        from .models.role import Role
        from .models.program import Program
        from .models.registration_sequence import RegistrationSequence
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register CLI commands
    register_commands(app)
    
    return app


def register_blueprints(app):
    """Register all blueprints"""
    from .auth.routes import auth_bp
    from .admin.routes import admin_bp
    from .teacher.routes import teacher_bp
    from .student.routes import student_bp
    from .marketing.routes import marketing_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(teacher_bp, url_prefix='/teacher')
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(marketing_bp)


def register_error_handlers(app):
    """Register error handlers"""
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500


def register_commands(app):
    """Register CLI commands"""
    @app.cli.command("init-db")
    def init_db():
        """Initialize the database"""
        db.create_all()
        print("✓ Database tables created.")
    
    @app.cli.command("seed-db")
    def seed_db():
        """Seed the database with initial data"""
        from seeders.roles_seeder import seed_roles
        from seeders.programs_seeder import seed_programs
        
        try:
            seed_roles()
            seed_programs()
            print("✓ Database seeded with initial data.")
        except Exception as e:
            print(f"✗ Error seeding database: {e}")
    
    @app.cli.command("create-admin")
    def create_admin():
        """Create a system admin user"""
        from .models.user import User
        from .models.role import Role
        from .extensions import bcrypt
        
        admin_role = Role.query.filter_by(name='System Admin').first()
        if not admin_role:
            print("✗ System Admin role not found. Please run seed-db first.")
            return
        
        # Check if admin already exists
        existing_admin = User.query.filter_by(email='admin@yca-abuja.com').first()
        if existing_admin:
            print("✗ Admin user already exists.")
            return
        
        admin = User(
            email='admin@yca-abuja.com',
            username='YCA/24/SYS/0001',
            first_name='System',
            surname='Administrator',
            gender='Male',
            password_hash=bcrypt.generate_password_hash('Admin@123').decode('utf-8'),
            is_active=True,
            email_verified=True
        )
        admin.roles.append(admin_role)
        
        db.session.add(admin)
        db.session.commit()
        
        print("✓ System admin user created:")
        print(f"   Email: admin@yca-abuja.com")
        print(f"   Password: Admin@123")
        print(f"   Username: YCA/24/SYS/0001")