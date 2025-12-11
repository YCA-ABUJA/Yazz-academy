from flask import (
    Blueprint, render_template, request, flash, redirect, 
    url_for, jsonify, current_app, session
)
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db, limiter
from app.models.user import User
from app.models.role import Role
from app.models.program import Program
from app.auth.forms import (
    LoginForm, RegistrationForm, ProfileUpdateForm, 
    PasswordChangeForm, ForgotPasswordForm, ResetPasswordForm
)
from app.services.registration_service import RegistrationService
from app.services.email_service import EmailService
import secrets
from datetime import datetime, timedelta
import json

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    """Login page"""
    if current_user.is_authenticated:
        return redirect_after_login()
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.verify_password(form.password.data):
            if user.is_suspended:
                flash('Your account is suspended. Please contact support.', 'danger')
                return render_template('auth/login.html', form=form)
            
            if not user.is_active:
                flash('Account is not active. Please contact administrator.', 'danger')
                return render_template('auth/login.html', form=form)
            
            if not user.email_verified:
                flash('Please verify your email before logging in.', 'warning')
                # Resend verification email
                user.generate_verification_token()
                EmailService.send_verification_email(user)
                db.session.commit()
                return render_template('auth/login.html', form=form)
            
            # Login successful
            login_user(user, remember=form.remember.data)
            user.record_login(request.remote_addr)
            
            flash('Login successful!', 'success')
            return redirect_after_login()
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('auth/login.html', form=form)

def redirect_after_login():
    """Redirect user based on their role after login"""
    if current_user.has_role('System Admin'):
        return redirect(url_for('admin.dashboard'))
    elif current_user.has_role('Teacher'):
        return redirect(url_for('teacher.dashboard'))
    elif current_user.has_role('Student'):
        return redirect(url_for('student.dashboard'))
    else:
        return redirect(url_for('marketing.index'))

@auth_bp.route('/logout')
@login_required
def logout():
    """Logout user"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per hour")
def register():
    """Registration page"""
    if current_user.is_authenticated:
        return redirect(url_for('marketing.index'))
    
    # Get programs for dropdown
    programs = Program.query.filter_by(is_active=True).all()
    
    form = RegistrationForm()
    form.selected_programs.choices = [(p.id, f"{p.name} - ₦{p.price_ngn:,.2f}") for p in programs]
    
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                # Prepare form data
                form_data = {
                    'email': form.email.data,
                    'password': form.password.data,
                    'confirm_password': form.confirm_password.data,
                    'surname': form.surname.data,
                    'first_name': form.first_name.data,
                    'middle_name': form.middle_name.data,
                    'gender': form.gender.data,
                    'phone': form.phone.data,
                    'address': form.address.data,
                    'state': form.state.data,
                    'country': form.country.data,
                    'facebook_handle': form.facebook_handle.data,
                    'twitter_handle': form.twitter_handle.data,
                    'github_handle': form.github_handle.data,
                    'linkedin_handle': form.linkedin_handle.data,
                    'bio': form.bio.data,
                    'qualifications': form.qualifications.data,
                    'selected_programs': [form.selected_programs.data],
                    'role': 'Student'  # Default role for registration
                }
                
                # Register user
                user, error = RegistrationService.register_user(
                    form_data=form_data,
                    photo_file=form.photo.data if form.photo.data else None,
                    resume_file=form.resume.data if form.resume.data else None,
                    remote_addr=request.remote_addr
                )
                
                if error:
                    flash(error, 'danger')
                    return render_template('auth/register.html', form=form, programs=programs)
                
                # Send verification email
                EmailService.send_verification_email(user)
                
                # Send admin notification
                EmailService.send_admin_notification(user)
                
                flash('Registration successful! Please check your email for verification.', 'success')
                return redirect(url_for('auth.login'))
                
            except Exception as e:
                current_app.logger.error(f"Registration error: {str(e)}")
                flash('An error occurred during registration. Please try again.', 'danger')
    
    return render_template('auth/register.html', form=form, programs=programs)

@auth_bp.route('/verify-email/<token>')
def verify_email(token):
    """Verify email with token"""
    if current_user.is_authenticated and current_user.email_verified:
        flash('Email already verified.', 'info')
        return redirect_after_login()
    
    user = User.query.filter_by(email_verification_token=token).first()
    
    if user:
        if user.verify_email(token):
            # Send welcome email
            EmailService.send_welcome_email(user)
            
            flash('Email verified successfully! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Invalid or expired verification link.', 'danger')
    else:
        flash('Invalid verification link.', 'danger')
    
    return redirect(url_for('auth.login'))

@auth_bp.route('/resend-verification', methods=['GET', 'POST'])
@limiter.limit("3 per hour")
def resend_verification():
    """Resend verification email"""
    if current_user.is_authenticated and current_user.email_verified:
        flash('Email already verified.', 'info')
        return redirect_after_login()
    
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            if user.email_verified:
                flash('Email already verified.', 'info')
                return redirect(url_for('auth.login'))
            
            # Check if verification was sent recently
            if (user.email_verification_sent_at and 
                (datetime.utcnow() - user.email_verification_sent_at).seconds < 300):
                flash('Verification email was recently sent. Please wait 5 minutes.', 'warning')
                return render_template('auth/resend_verification.html')
            
            # Generate new token and send email
            user.generate_verification_token()
            EmailService.send_verification_email(user)
            
            flash('Verification email sent! Please check your inbox.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Email not found.', 'danger')
    
    return render_template('auth/resend_verification.html')

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
@limiter.limit("5 per hour")
def forgot_password():
    """Forgot password page"""
    if current_user.is_authenticated:
        return redirect_after_login()
    
    form = ForgotPasswordForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user:
            # Generate reset token
            reset_token = secrets.token_urlsafe(32)
            user.password_reset_token = reset_token
            user.password_reset_sent_at = datetime.utcnow()
            db.session.commit()
            
            # Send reset email
            EmailService.send_password_reset_email(user, reset_token)
            
            flash('Password reset instructions sent to your email.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Email not found.', 'danger')
    
    return render_template('auth/forgot_password.html', form=form)

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
@limiter.limit("5 per hour")
def reset_password(token):
    """Reset password page"""
    if current_user.is_authenticated:
        return redirect_after_login()
    
    user = User.query.filter_by(password_reset_token=token).first()
    
    if not user or not user.password_reset_sent_at:
        flash('Invalid or expired reset link.', 'danger')
        return redirect(url_for('auth.forgot_password'))
    
    # Check if token expired (1 hour)
    if (datetime.utcnow() - user.password_reset_sent_at).seconds > 3600:
        flash('Reset link has expired. Please request a new one.', 'danger')
        return redirect(url_for('auth.forgot_password'))
    
    form = ResetPasswordForm()
    
    if form.validate_on_submit():
        # Update password
        user.password = form.password.data
        user.password_reset_token = None
        user.password_reset_sent_at = None
        db.session.commit()
        
        flash('Password reset successful! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', form=form, token=token)

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile page"""
    form = ProfileUpdateForm(obj=current_user)
    
    if form.validate_on_submit():
        try:
            form_data = {
                'surname': form.surname.data,
                'first_name': form.first_name.data,
                'middle_name': form.middle_name.data,
                'gender': form.gender.data,
                'phone': form.phone.data,
                'address': form.address.data,
                'state': form.state.data,
                'country': form.country.data,
                'facebook_handle': form.facebook_handle.data,
                'twitter_handle': form.twitter_handle.data,
                'github_handle': form.github_handle.data,
                'linkedin_handle': form.linkedin_handle.data,
                'bio': form.bio.data,
                'qualifications': form.qualifications.data
            }
            
            user, error = RegistrationService.update_user_profile(
                user_id=current_user.id,
                form_data=form_data,
                photo_file=form.photo.data if form.photo.data else None,
                resume_file=form.resume.data if form.resume.data else None
            )
            
            if error:
                flash(error, 'danger')
            else:
                flash('Profile updated successfully!', 'success')
                return redirect(url_for('auth.profile'))
                
        except Exception as e:
            current_app.logger.error(f"Profile update error: {str(e)}")
            flash('An error occurred. Please try again.', 'danger')
    
    return render_template('auth/profile.html', form=form)

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change password page"""
    form = PasswordChangeForm()
    
    if form.validate_on_submit():
        if not current_user.verify_password(form.current_password.data):
            flash('Current password is incorrect.', 'danger')
            return render_template('auth/change_password.html', form=form)
        
        try:
            current_user.password = form.new_password.data
            db.session.commit()
            
            flash('Password changed successfully!', 'success')
            return redirect(url_for('auth.profile'))
            
        except ValueError as e:
            flash(str(e), 'danger')
        except Exception as e:
            current_app.logger.error(f"Password change error: {str(e)}")
            flash('An error occurred. Please try again.', 'danger')
    
    return render_template('auth/change_password.html', form=form)

@auth_bp.route('/api/check-email')
@limiter.limit("10 per minute")
def check_email():
    """Check if email is available (for AJAX validation)"""
    email = request.args.get('email', '')
    
    if not email:
        return jsonify({'available': False, 'message': 'Email is required'})
    
    user = User.query.filter_by(email=email).first()
    
    if user:
        return jsonify({'available': False, 'message': 'Email already registered'})
    else:
        return jsonify({'available': True, 'message': 'Email is available'})

@auth_bp.route('/api/validate-password')
@limiter.limit("10 per minute")
def validate_password():
    """Validate password strength (for AJAX validation)"""
    password = request.args.get('password', '')
    
    if len(password) < 8:
        return jsonify({'valid': False, 'message': 'Password must be at least 8 characters'})
    
    if not any(char.isdigit() for char in password):
        return jsonify({'valid': False, 'message': 'Password must contain at least one number'})
    
    if not any(char.isupper() for char in password):
        return jsonify({'valid': False, 'message': 'Password must contain at least one uppercase letter'})
    
    if not any(char.islower() for char in password):
        return jsonify({'valid': False, 'message': 'Password must contain at least one lowercase letter'})
    
    special_chars = '!@#$%^&*()_+-=[]{}|;:,.<>?'
    if not any(char in special_chars for char in password):
        return jsonify({'valid': False, 'message': 'Password must contain at least one special character'})
    
    return jsonify({'valid': True, 'message': 'Password is strong'})