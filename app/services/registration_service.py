from datetime import datetime
from app.extensions import db
from app.models.user import User
from app.models.role import Role
from app.models.registration_sequence import RegistrationSequence
from app.services.username_generator import UsernameGenerator
from app.services.file_upload_service import FileUploadService
import json

class RegistrationService:
    """Service for handling user registration"""
    
    @classmethod
    def register_user(cls, form_data, photo_file=None, resume_file=None, remote_addr=None):
        """
        Register a new user with all required fields
        
        Args:
            form_data: Dictionary containing form data
            photo_file: Uploaded photo file
            resume_file: Uploaded resume file
            remote_addr: User's IP address
            
        Returns:
            tuple: (user_object, error_message)
        """
        try:
            # Validate required fields
            validation_error = cls._validate_registration_data(form_data)
            if validation_error:
                return None, validation_error
            
            # Generate username
            username, username_error = cls._generate_username(form_data)
            if username_error:
                return None, username_error
            
            # Validate email uniqueness
            if User.query.filter_by(email=form_data['email']).first():
                return None, "Email already registered"
            
            # Create user object
            user = User(
                username=username,
                email=form_data['email'],
                phone=form_data.get('phone', ''),
                surname=form_data['surname'],
                first_name=form_data['first_name'],
                middle_name=form_data.get('middle_name', ''),
                gender=form_data['gender'],
                address=form_data.get('address', ''),
                state=form_data.get('state', ''),
                country=form_data.get('country', 'Nigeria'),
                facebook_handle=form_data.get('facebook_handle', ''),
                twitter_handle=form_data.get('twitter_handle', ''),
                github_handle=form_data.get('github_handle', ''),
                linkedin_handle=form_data.get('linkedin_handle', ''),
                bio=form_data.get('bio', '')
            )
            
            # Set password with validation
            try:
                user.password = form_data['password']
            except ValueError as e:
                return None, str(e)
            
            # Handle file uploads
            if photo_file:
                photo_path, photo_error = FileUploadService.validate_and_save_photo(photo_file)
                if photo_error:
                    return None, photo_error
                user.photo_path = photo_path
            
            if resume_file:
                resume_path, resume_error = FileUploadService.validate_and_save_resume(resume_file)
                if resume_error:
                    return None, resume_error
                user.resume_path = resume_path
            
            # Parse educational qualifications
            if 'qualifications' in form_data:
                user.qualifications = cls._parse_qualifications(form_data['qualifications'])
            
            # Parse selected programs
            if 'selected_programs' in form_data:
                user.selected_programs = cls._parse_selected_programs(form_data['selected_programs'])
            
            # Assign role (default to Student if not specified)
            role_name = form_data.get('role', 'Student')
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                return None, f"Invalid role: {role_name}"
            
            user.roles.append(role)
            
            # Generate email verification token
            user.generate_verification_token()
            
            # Save user to database
            db.session.add(user)
            db.session.commit()
            
            # Record registration IP
            if remote_addr:
                user.last_login_ip = remote_addr
            
            return user, None
            
        except Exception as e:
            db.session.rollback()
            return None, f"Registration error: {str(e)}"
    
    @classmethod
    def _validate_registration_data(cls, form_data):
        """Validate all registration data"""
        required_fields = [
            'email', 'password', 'confirm_password',
            'surname', 'first_name', 'gender'
        ]
        
        for field in required_fields:
            if not form_data.get(field):
                return f"{field.replace('_', ' ').title()} is required"
        
        # Email validation
        if not User.validate_email(form_data['email']):
            return "Invalid email format"
        
        # Password confirmation
        if form_data['password'] != form_data['confirm_password']:
            return "Passwords do not match"
        
        # Gender validation
        if form_data['gender'] not in ['Male', 'Female', 'Other']:
            return "Invalid gender selection"
        
        # Phone validation (if provided)
        if form_data.get('phone'):
            if not User.validate_phone(form_data['phone']):
                return "Invalid phone number format"
        
        # Bio length validation
        if form_data.get('bio') and len(form_data['bio']) > 1000:
            return "Bio must be 1000 characters or less"
        
        return None
    
    @classmethod
    def _generate_username(cls, form_data):
        """Generate username based on role and selected programs"""
        role_name = form_data.get('role', 'Student')
        
        # For student registration, need program info
        if role_name == 'Student':
            selected_programs = form_data.get('selected_programs', [])
            if not selected_programs:
                return None, "At least one program must be selected for student registration"
            
            # Use the first selected program for username generation
            program_id = selected_programs[0] if isinstance(selected_programs, list) else selected_programs
            # In production, you would fetch the program name from database
            program_name = form_data.get('program_name', 'General')  # This should come from form
        
        # For other roles, use appropriate defaults
        elif role_name == 'Teacher':
            program_name = form_data.get('specialization', 'General')
        else:
            program_name = None
        
        try:
            username = UsernameGenerator.generate_username(
                year=datetime.now().year % 100,
                role_name=role_name,
                program_name=program_name,
                cohort=form_data.get('cohort', 'A')
            )
            return username, None
        except Exception as e:
            return None, f"Username generation error: {str(e)}"
    
    @classmethod
    def _parse_qualifications(cls, qualifications_data):
        """Parse educational qualifications from form data"""
        if isinstance(qualifications_data, str):
            try:
                return json.loads(qualifications_data)
            except:
                return []
        elif isinstance(qualifications_data, list):
            return qualifications_data
        return []
    
    @classmethod
    def _parse_selected_programs(cls, programs_data):
        """Parse selected programs from form data"""
        if isinstance(programs_data, str):
            try:
                return json.loads(programs_data)
            except:
                return []
        elif isinstance(programs_data, list):
            return [str(pid) for pid in programs_data]
        return []
    
    @classmethod
    def update_user_profile(cls, user_id, form_data, photo_file=None, resume_file=None):
        """
        Update user profile information
        
        Args:
            user_id: User ID to update
            form_data: Dictionary containing updated form data
            photo_file: New photo file (optional)
            resume_file: New resume file (optional)
            
        Returns:
            tuple: (user_object, error_message)
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return None, "User not found"
            
            # Update basic information
            if 'surname' in form_data:
                user.surname = form_data['surname']
            if 'first_name' in form_data:
                user.first_name = form_data['first_name']
            if 'middle_name' in form_data:
                user.middle_name = form_data['middle_name']
            if 'gender' in form_data:
                user.gender = form_data['gender']
            if 'phone' in form_data:
                user.phone = form_data['phone']
            if 'address' in form_data:
                user.address = form_data['address']
            if 'state' in form_data:
                user.state = form_data['state']
            if 'country' in form_data:
                user.country = form_data['country']
            if 'bio' in form_data:
                user.bio = form_data['bio'][:1000]  # Enforce length limit
            
            # Update social media handles
            if 'facebook_handle' in form_data:
                user.facebook_handle = form_data['facebook_handle']
            if 'twitter_handle' in form_data:
                user.twitter_handle = form_data['twitter_handle']
            if 'github_handle' in form_data:
                user.github_handle = form_data['github_handle']
            if 'linkedin_handle' in form_data:
                user.linkedin_handle = form_data['linkedin_handle']
            
            # Update qualifications
            if 'qualifications' in form_data:
                user.qualifications = cls._parse_qualifications(form_data['qualifications'])
            
            # Handle file uploads
            if photo_file:
                # Delete old photo if exists
                if user.photo_path:
                    FileUploadService.delete_file(user.photo_path)
                
                photo_path, photo_error = FileUploadService.validate_and_save_photo(photo_file)
                if photo_error:
                    return None, photo_error
                user.photo_path = photo_path
            
            if resume_file:
                # Delete old resume if exists
                if user.resume_path:
                    FileUploadService.delete_file(user.resume_path)
                
                resume_path, resume_error = FileUploadService.validate_and_save_resume(resume_file)
                if resume_error:
                    return None, resume_error
                user.resume_path = resume_path
            
            db.session.commit()
            return user, None
            
        except Exception as e:
            db.session.rollback()
            return None, f"Profile update error: {str(e)}"