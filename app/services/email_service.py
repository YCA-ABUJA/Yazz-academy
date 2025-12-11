from flask_mail import Message
from app.extensions import mail
from flask import current_app, url_for, render_template
from threading import Thread
import time

class EmailService:
    """Service for sending emails asynchronously"""
    
    @staticmethod
    def send_async_email(app, msg):
        """Send email in background thread"""
        with app.app_context():
            try:
                mail.send(msg)
                current_app.logger.info(f"Email sent successfully to {msg.recipients}")
            except Exception as e:
                current_app.logger.error(f"Failed to send email: {str(e)}")
    
    @classmethod
    def send_email(cls, subject, recipients, text_body, html_body=None):
        """
        Send email
        
        Args:
            subject: Email subject
            recipients: List of recipient emails
            text_body: Plain text email body
            html_body: HTML email body (optional)
        """
        msg = Message(
            subject=subject,
            recipients=recipients,
            body=text_body,
            html=html_body,
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        # Send email in background thread
        Thread(target=cls.send_async_email, args=(current_app._get_current_object(), msg)).start()
    
    @classmethod
    def send_verification_email(cls, user):
        """Send email verification link"""
        verification_url = url_for(
            'auth.verify_email',
            token=user.email_verification_token,
            _external=True
        )
        
        subject = "Verify Your Email - Yazz Communication Academy"
        
        text_body = f"""
        Welcome to Yazz Communication Academy!
        
        Please verify your email address by clicking the link below:
        {verification_url}
        
        This link will expire in 7 days.
        
        If you did not create an account, please ignore this email.
        
        Best regards,
        Yazz Communication Academy Team
        """
        
        html_body = render_template(
            'emails/verification.html',
            user=user,
            verification_url=verification_url
        )
        
        cls.send_email(subject, [user.email], text_body, html_body)
    
    @classmethod
    def send_welcome_email(cls, user):
        """Send welcome email after successful verification"""
        subject = "Welcome to Yazz Communication Academy!"
        
        text_body = f"""
        Dear {user.first_name},
        
        Welcome to Yazz Communication Academy! Your account has been successfully verified.
        
        Your username: {user.username}
        
        You can now log in to your dashboard and start your learning journey.
        
        Login here: {url_for('auth.login', _external=True)}
        
        If you have any questions, please contact our support team at services@yca-abuja.com
        
        Best regards,
        Yazz Communication Academy Team
        """
        
        html_body = render_template(
            'emails/welcome.html',
            user=user,
            login_url=url_for('auth.login', _external=True)
        )
        
        cls.send_email(subject, [user.email], text_body, html_body)
    
    @classmethod
    def send_password_reset_email(cls, user, reset_token):
        """Send password reset email"""
        reset_url = url_for(
            'auth.reset_password',
            token=reset_token,
            _external=True
        )
        
        subject = "Password Reset Request - Yazz Communication Academy"
        
        text_body = f"""
        You have requested to reset your password for your Yazz Communication Academy account.
        
        To reset your password, click the link below:
        {reset_url}
        
        This link will expire in 1 hour.
        
        If you did not request a password reset, please ignore this email.
        
        Best regards,
        Yazz Communication Academy Team
        """
        
        html_body = render_template(
            'emails/password_reset.html',
            user=user,
            reset_url=reset_url
        )
        
        cls.send_email(subject, [user.email], text_body, html_body)
    
    @classmethod
    def send_admin_notification(cls, user, admin_emails=None):
        """Send notification to admins about new registration"""
        if not admin_emails:
            admin_emails = ['admin@yca-abuja.com']  # Default admin email
        
        subject = f"New User Registration: {user.get_full_name()}"
        
        text_body = f"""
        New user registration details:
        
        Name: {user.get_full_name()}
        Email: {user.email}
        Username: {user.username}
        Role: {', '.join([role.name for role in user.roles])}
        Registration Date: {user.created_at.strftime('%Y-%m-%d %H:%M:%S')}
        
        Please review and activate the account if necessary.
        """
        
        cls.send_email(subject, admin_emails, text_body)