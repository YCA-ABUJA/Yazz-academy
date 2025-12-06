from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required
from app.extensions import db
from app.models.user import User
from app.models.role import Role

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
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
                    return redirect(url_for('admin.dashboard'))
                elif user.has_role('Teacher'):
                    return redirect(url_for('teacher.dashboard'))
                elif user.has_role('Student'):
                    return redirect(url_for('student.dashboard'))
                else:
                    return redirect(url_for('marketing.index'))
            else:
                flash('Account is disabled. Please contact administrator.', 'danger')
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Logout user"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page"""
    # This will be implemented fully in next steps
    return render_template('auth/register.html')

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Forgot password page"""
    return render_template('auth/forgot_password.html')