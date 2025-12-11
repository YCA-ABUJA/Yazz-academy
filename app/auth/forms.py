from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import (
    StringField, PasswordField, EmailField, SelectField, 
    TextAreaField, MultipleFileField, DateField, BooleanField,
    SubmitField, ValidationError
)
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional
from app.models.user import User

class LoginForm(FlaskForm):
    """Login form"""
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    """User registration form"""
    # Personal Information
    surname = StringField('Surname', validators=[DataRequired(), Length(max=100)])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=100)])
    middle_name = StringField('Middle Name (Optional)', validators=[Optional(), Length(max=100)])
    gender = SelectField('Gender', choices=[
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    
    # Contact Information
    email = EmailField('Email Address', validators=[DataRequired(), Email(), Length(max=120)])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(max=20)])
    address = TextAreaField('Address', validators=[DataRequired()])
    state = StringField('State', validators=[DataRequired(), Length(max=100)])
    country = StringField('Country', validators=[DataRequired(), Length(max=100)])
    
    # Social Media
    facebook_handle = StringField('Facebook Handle', validators=[Optional(), Length(max=100)])
    twitter_handle = StringField('Twitter Handle', validators=[Optional(), Length(max=100)])
    github_handle = StringField('GitHub Handle', validators=[Optional(), Length(max=100)])
    linkedin_handle = StringField('LinkedIn Handle', validators=[Optional(), Length(max=100)])
    
    # Profile
    photo = FileField('Profile Photo', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    resume = FileField('CV/Resume', validators=[
        Optional(),
        FileAllowed(['pdf', 'doc', 'docx'], 'PDF or Word documents only!')
    ])
    bio = TextAreaField('Short Bio (Max 1000 characters)', validators=[
        Optional(), 
        Length(max=1000)
    ])
    
    # Educational Qualifications (as JSON string)
    qualifications = TextAreaField('Educational Qualifications (JSON format)', validators=[Optional()])
    
    # Programs/Courses
    selected_programs = SelectField('Select Program(s)', coerce=int, validators=[DataRequired()])
    
    # Authentication
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters'),
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    
    # Terms agreement
    accept_terms = BooleanField('I accept the Terms of Service and Privacy Policy', 
                               validators=[DataRequired()])
    
    submit = SubmitField('Register')
    
    def validate_email(self, field):
        """Check if email is already registered"""
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered. Please use a different email.')
    
    def validate_phone(self, field):
        """Validate phone number format"""
        if not User.validate_phone(field.data):
            raise ValidationError('Invalid phone number format. Use format: +234XXXXXXXXXX')
    
    def validate_password(self, field):
        """Validate password complexity"""
        password = field.data
        
        # Check for at least one number
        if not any(char.isdigit() for char in password):
            raise ValidationError('Password must contain at least one number')
        
        # Check for at least one uppercase letter
        if not any(char.isupper() for char in password):
            raise ValidationError('Password must contain at least one uppercase letter')
        
        # Check for at least one lowercase letter
        if not any(char.islower() for char in password):
            raise ValidationError('Password must contain at least one lowercase letter')
        
        # Check for at least one special character
        special_chars = '!@#$%^&*()_+-=[]{}|;:,.<>?'
        if not any(char in special_chars for char in password):
            raise ValidationError('Password must contain at least one special character')
    
    def validate_qualifications(self, field):
        """Validate qualifications JSON format"""
        if field.data:
            import json
            try:
                json.loads(field.data)
            except json.JSONDecodeError:
                raise ValidationError('Invalid JSON format for qualifications')

class ProfileUpdateForm(FlaskForm):
    """Profile update form"""
    # Personal Information
    surname = StringField('Surname', validators=[DataRequired(), Length(max=100)])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=100)])
    middle_name = StringField('Middle Name (Optional)', validators=[Optional(), Length(max=100)])
    gender = SelectField('Gender', choices=[
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    
    # Contact Information
    phone = StringField('Phone Number', validators=[DataRequired(), Length(max=20)])
    address = TextAreaField('Address', validators=[DataRequired()])
    state = StringField('State', validators=[DataRequired(), Length(max=100)])
    country = StringField('Country', validators=[DataRequired(), Length(max=100)])
    
    # Social Media
    facebook_handle = StringField('Facebook Handle', validators=[Optional(), Length(max=100)])
    twitter_handle = StringField('Twitter Handle', validators=[Optional(), Length(max=100)])
    github_handle = StringField('GitHub Handle', validators=[Optional(), Length(max=100)])
    linkedin_handle = StringField('LinkedIn Handle', validators=[Optional(), Length(max=100)])
    
    # Profile
    photo = FileField('Profile Photo', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    resume = FileField('CV/Resume', validators=[
        Optional(),
        FileAllowed(['pdf', 'doc', 'docx'], 'PDF or Word documents only!')
    ])
    bio = TextAreaField('Short Bio (Max 1000 characters)', validators=[
        Optional(), 
        Length(max=1000)
    ])
    
    # Educational Qualifications
    qualifications = TextAreaField('Educational Qualifications (JSON format)', validators=[Optional()])
    
    submit = SubmitField('Update Profile')
    
    def validate_phone(self, field):
        """Validate phone number format"""
        if not User.validate_phone(field.data):
            raise ValidationError('Invalid phone number format. Use format: +234XXXXXXXXXX')
    
    def validate_qualifications(self, field):
        """Validate qualifications JSON format"""
        if field.data:
            import json
            try:
                json.loads(field.data)
            except json.JSONDecodeError:
                raise ValidationError('Invalid JSON format for qualifications')

class PasswordChangeForm(FlaskForm):
    """Password change form"""
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters'),
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('new_password', message='Passwords must match')
    ])
    submit = SubmitField('Change Password')
    
    def validate_new_password(self, field):
        """Validate password complexity"""
        password = field.data
        
        # Check for at least one number
        if not any(char.isdigit() for char in password):
            raise ValidationError('Password must contain at least one number')
        
        # Check for at least one uppercase letter
        if not any(char.isupper() for char in password):
            raise ValidationError('Password must contain at least one uppercase letter')
        
        # Check for at least one lowercase letter
        if not any(char.islower() for char in password):
            raise ValidationError('Password must contain at least one lowercase letter')
        
        # Check for at least one special character
        special_chars = '!@#$%^&*()_+-=[]{}|;:,.<>?'
        if not any(char in special_chars for char in password):
            raise ValidationError('Password must contain at least one special character')

class ForgotPasswordForm(FlaskForm):
    """Forgot password form"""
    email = EmailField('Email Address', validators=[DataRequired(), Email()])
    submit = SubmitField('Send Reset Link')

class ResetPasswordForm(FlaskForm):
    """Reset password form"""
    password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters'),
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Reset Password')
    
    def validate_password(self, field):
        """Validate password complexity"""
        password = field.data
        
        # Check for at least one number
        if not any(char.isdigit() for char in password):
            raise ValidationError('Password must contain at least one number')
        
        # Check for at least one uppercase letter
        if not any(char.isupper() for char in password):
            raise ValidationError('Password must contain at least one uppercase letter')
        
        # Check for at least one lowercase letter
        if not any(char.islower() for char in password):
            raise ValidationError('Password must contain at least one lowercase letter')
        
        # Check for at least one special character
        special_chars = '!@#$%^&*()_+-=[]{}|;:,.<>?'
        if not any(char in special_chars for char in password):
            raise ValidationError('Password must contain at least one special character')