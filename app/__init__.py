from flask import Flask
from config import config
from .extensions import init_extensions
from datetime import datetime
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
    
     # Register template filters
    @app.template_filter('datetime_format')
    def datetime_format(value, format='%Y-%m-%d %H:%M'):
        if value is None:
            return ""
        return value.strftime(format)
    
    @app.context_processor
    def utility_processor():
        def now():
            return datetime.now()
        return dict(now=now)

    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register CLI commands
    from app.commands import init_db_command, create_admin, seed_db
    app.cli.add_command(init_db_command)
    app.cli.add_command(create_admin)
    app.cli.add_command(seed_db)
    
    return app


def register_blueprints(app):
    """Register all blueprints"""
    from .auth.routes import auth_bp
    from .admin.routes import admin_bp
    from .teacher.routes import teacher_bp
    from .student.routes import student_bp
    from .marketing.routes import marketing_bp
    from .dashboard.routes import dashboard_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(teacher_bp, url_prefix='/teacher')
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(marketing_bp)
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')


def register_error_handlers(app):
    """Register error handlers"""
    @app.errorhandler(404)
    def page_not_found(e):
        return 'Page not found', 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return 'Internal server error', 500