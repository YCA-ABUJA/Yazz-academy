"""
Yazz Communication Academy LMS - Complete Application
Single file for simplicity, will refactor later
"""
import os
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
import pymysql
pymysql.install_as_MySQLdb()

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()

def create_app():
    """Application factory"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database configuration for XAMPP
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'mysql+pymysql://root:@localhost:3306/yazz_academy')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_recycle': 280,
        'pool_pre_ping': True,
    }
    
    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    
    # Login manager configuration
    login_manager.login_view = 'login'
    login_manager.login_message_category = 'info'
    
    # ==================== MODELS ====================
    
    # Association table for user roles
    user_roles = db.Table('user_roles',
        db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
        db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True),
        db.Column('assigned_at', db.DateTime, default=datetime.utcnow)
    )
    
    class Role(db.Model):
        """Role model for RBAC"""
        __tablename__ = 'roles'
        
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(50), unique=True, nullable=False)
        description = db.Column(db.String(200))
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        
        def __repr__(self):
            return f'<Role {self.name}>'
    
    class User(db.Model, UserMixin):
        """User model for all roles"""
        __tablename__ = 'users'
        
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(50), unique=True, nullable=False)
        email = db.Column(db.String(120), unique=True, nullable=False)
        surname = db.Column(db.String(100), nullable=False)
        first_name = db.Column(db.String(100), nullable=False)
        middle_name = db.Column(db.String(100))
        gender = db.Column(db.String(10), nullable=False)
        phone = db.Column(db.String(20))
        password_hash = db.Column(db.String(128), nullable=False)
        is_active = db.Column(db.Boolean, default=True)
        email_verified = db.Column(db.Boolean, default=False)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        
        # Relationships
        roles = db.relationship('Role', secondary=user_roles, backref='users')
        
        def __repr__(self):
            return f'<User {self.username}>'
        
        @property
        def password(self):
            raise AttributeError('password is not readable')
        
        @password.setter
        def password(self, password):
            self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        
        def verify_password(self, password):
            return bcrypt.check_password_hash(self.password_hash, password)
        
        def has_role(self, role_name):
            """Check if user has a specific role"""
            return any(role.name == role_name for role in self.roles)
    
    class Program(db.Model):
        """Program/Course model"""
        __tablename__ = 'programs'
        
        id = db.Column(db.Integer, primary_key=True)
        code = db.Column(db.String(20), unique=True, nullable=False)
        name = db.Column(db.String(200), nullable=False)
        description = db.Column(db.Text)
        category = db.Column(db.String(100))
        duration_weeks = db.Column(db.Integer)
        price_ngn = db.Column(db.Numeric(10, 2))
        is_active = db.Column(db.Boolean, default=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        
        def __repr__(self):
            return f'<Program {self.code}: {self.name}>'
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # ==================== ROUTES ====================
    
    @app.route('/')
    def index():
        """Home page"""
        programs = Program.query.filter_by(is_active=True).all() if Program.query.first() else []
        return render_template('index.html', programs=programs)
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """Login page"""
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            
            user = User.query.filter_by(email=email).first()
            
            if user and user.verify_password(password):
                if user.is_active:
                    login_user(user, remember=True)
                    flash('Login successful!', 'success')
                    
                    # Redirect based on role
                    if user.has_role('System Admin'):
                        return redirect(url_for('admin_dashboard'))
                    else:
                        return redirect(url_for('dashboard'))
                else:
                    flash('Account is disabled. Contact administrator.', 'danger')
            else:
                flash('Invalid email or password.', 'danger')
        
        return render_template('login.html')
    
    @app.route('/logout')
    @login_required
    def logout():
        """Logout user"""
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('index'))
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        """Registration page"""
        if request.method == 'POST':
            # Basic registration logic
            email = request.form.get('email')
            password = request.form.get('password')
            first_name = request.form.get('first_name')
            surname = request.form.get('surname')
            gender = request.form.get('gender')
            
            # Check if user exists
            if User.query.filter_by(email=email).first():
                flash('Email already registered.', 'danger')
                return redirect(url_for('register'))
            
            # Create user
            user = User(
                email=email,
                username=email.split('@')[0],  # Temporary username
                first_name=first_name,
                surname=surname,
                gender=gender,
                password=password,
                is_active=True
            )
            
            # Assign student role
            student_role = Role.query.filter_by(name='Student').first()
            if student_role:
                user.roles.append(student_role)
            
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        
        return render_template('register.html')
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        """User dashboard"""
        return render_template('dashboard.html', user=current_user)
    
    @app.route('/admin')
    @login_required
    def admin_dashboard():
        """Admin dashboard"""
        if not current_user.has_role('System Admin'):
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('dashboard'))
        
        stats = {
            'total_users': User.query.count(),
            'total_programs': Program.query.count(),
            'active_users': User.query.filter_by(is_active=True).count(),
        }
        
        return render_template('admin.html', stats=stats)
    
    @app.route('/courses')
    def courses():
        """Courses catalog"""
        programs = Program.query.filter_by(is_active=True).all()
        return render_template('courses.html', programs=programs)
    
    @app.route('/about')
    def about():
        """About page"""
        return render_template('about.html')
    
    @app.route('/contact', methods=['GET', 'POST'])
    def contact():
        """Contact page"""
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            message = request.form.get('message')
            
            # Here you would typically save to database or send email
            flash('Thank you for your message! We will contact you soon.', 'success')
            return redirect(url_for('contact'))
        
        return render_template('contact.html')
    
    # ==================== API ENDPOINTS ====================
    
    @app.route('/api/health')
    def health_check():
        """Health check endpoint"""
        return jsonify({'status': 'healthy', 'service': 'yazz-academy-lms'})
    
    @app.route('/api/stats')
    @login_required
    def get_stats():
        """Get system statistics"""
        if not current_user.has_role('System Admin'):
            return jsonify({'error': 'Unauthorized'}), 403
        
        stats = {
            'total_users': User.query.count(),
            'total_programs': Program.query.count(),
            'active_users': User.query.filter_by(is_active=True).count(),
            'roles': [role.name for role in Role.query.all()]
        }
        
        return jsonify(stats)
    
    # ==================== CLI COMMANDS ====================
    
    @app.cli.command('init-db')
    def init_db():
        """Initialize database with seed data"""
        with app.app_context():
            # Create tables
            db.create_all()
            print("✓ Database tables created")
            
            # Create roles
            roles = [
                ('System Admin', 'Full system administrator'),
                ('Head of School', 'Head of the academy'),
                ('Teacher', 'Course instructor'),
                ('Student', 'Registered student'),
                ('Guest', 'Guest user'),
            ]
            
            for name, description in roles:
                if not Role.query.filter_by(name=name).first():
                    role = Role(name=name, description=description)
                    db.session.add(role)
                    print(f"  Added role: {name}")
            
            db.session.commit()
            
            # Create admin user
            if not User.query.filter_by(email='admin@yca-abuja.com').first():
                admin = User(
                    username='admin',
                    email='admin@yca-abuja.com',
                    surname='Admin',
                    first_name='System',
                    gender='Male',
                    password='Admin@123',
                    is_active=True,
                    email_verified=True
                )
                
                # Assign admin role
                admin_role = Role.query.filter_by(name='System Admin').first()
                if admin_role:
                    admin.roles.append(admin_role)
                
                db.session.add(admin)
                print("  Added admin user: admin@yca-abuja.com")
            
            # Create sample programs
            programs = [
                ('PYT', 'Python Programming', 'Tech & Digital Skills', 13, 95000.00,
                 'Learn Python from basics to advanced concepts with hands-on projects.'),
                ('WD', 'Web Development', 'Tech & Digital Skills', 14, 120000.00,
                 'Master full-stack web development with modern frameworks and tools.'),
                ('DA', 'Data Analytics', 'Tech & Digital Skills', 8, 90000.00,
                 'Learn to analyze and visualize data to drive business decisions.'),
                ('CYF', 'Cybersecurity Fundamentals', 'Tech & Digital Skills', 4, 60000.00,
                 'Introduction to cybersecurity concepts and best practices.'),
                ('PS', 'Public Speaking', 'Communication & Soft Skills', 1, 65000.00,
                 'Develop confident public speaking skills for professional success.'),
            ]
            
            for code, name, category, weeks, price, desc in programs:
                if not Program.query.filter_by(code=code).first():
                    program = Program(
                        code=code,
                        name=name,
                        category=category,
                        duration_weeks=weeks,
                        price_ngn=price,
                        description=desc
                    )
                    db.session.add(program)
                    print(f"  Added program: {name}")
            
            db.session.commit()
            print("\n✓ Database initialization complete!")
            print("\nAdmin credentials:")
            print("  Email: admin@yca-abuja.com")
            print("  Password: Admin@123")
            print("\nAccess the application at: http://localhost:5000")
    
    @app.cli.command('create-user')
    def create_user():
        """Create a new user"""
        with app.app_context():
            email = input("Email: ")
            first_name = input("First Name: ")
            surname = input("Surname: ")
            password = input("Password: ")
            role_name = input("Role (Student/Teacher/Admin): ")
            
            # Check if user exists
            if User.query.filter_by(email=email).first():
                print("User already exists!")
                return
            
            # Create user
            user = User(
                email=email,
                username=email.split('@')[0],
                first_name=first_name,
                surname=surname,
                gender='Male',  # Default
                password=password,
                is_active=True
            )
            
            # Assign role
            role = Role.query.filter_by(name=role_name).first()
            if role:
                user.roles.append(role)
            
            db.session.add(user)
            db.session.commit()
            
            print(f"User created: {email}")
    
    return app

# Create the application
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)