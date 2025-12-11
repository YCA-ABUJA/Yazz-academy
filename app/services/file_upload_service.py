import os
import uuid
from PIL import Image
from werkzeug.utils import secure_filename
from flask import current_app
import magic
from pathlib import Path

class FileUploadService:
    """Service for handling file uploads with validation and processing"""
    
    # Allowed MIME types
    ALLOWED_IMAGE_TYPES = {
        'image/jpeg': 'jpg',
        'image/png': 'png',
        'image/gif': 'gif',
        'image/webp': 'webp'
    }
    
    ALLOWED_DOC_TYPES = {
        'application/pdf': 'pdf',
        'application/msword': 'doc',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx'
    }
    
    # File size limits (in bytes)
    MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
    MAX_RESUME_SIZE = 10 * 1024 * 1024  # 10MB
    
    @classmethod
    def validate_file(cls, file, file_type='image'):
        """
        Validate uploaded file
        
        Args:
            file: FileStorage object
            file_type: 'image' or 'document'
            
        Returns:
            tuple: (is_valid, error_message, mime_type)
        """
        if not file:
            return False, 'No file uploaded', None
        
        # Check file size
        max_size = cls.MAX_IMAGE_SIZE if file_type == 'image' else cls.MAX_RESUME_SIZE
        if len(file.read()) > max_size:
            file.seek(0)  # Reset file pointer
            return False, f'File size exceeds {max_size // (1024*1024)}MB limit', None
        file.seek(0)  # Reset file pointer
        
        # Check MIME type
        mime = magic.Magic(mime=True)
        mime_type = mime.from_buffer(file.read(1024))
        file.seek(0)
        
        allowed_types = cls.ALLOWED_IMAGE_TYPES if file_type == 'image' else cls.ALLOWED_DOC_TYPES
        if mime_type not in allowed_types:
            return False, f'Invalid file type. Allowed: {", ".join(allowed_types.keys())}', mime_type
        
        return True, None, mime_type
    
    @classmethod
    def save_file(cls, file, mime_type, upload_type='photo'):
        """
        Save uploaded file with secure naming
        
        Args:
            file: FileStorage object
            mime_type: Detected MIME type
            upload_type: 'photo' or 'resume'
            
        Returns:
            str: Saved file path relative to upload folder
        """
        # Determine upload directory
        if upload_type == 'photo':
            upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'photos')
            allowed_types = cls.ALLOWED_IMAGE_TYPES
        else:  # resume
            upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'resumes')
            allowed_types = cls.ALLOWED_DOC_TYPES
        
        # Ensure directory exists
        Path(upload_dir).mkdir(parents=True, exist_ok=True)
        
        # Generate secure filename
        original_filename = secure_filename(file.filename)
        file_ext = allowed_types.get(mime_type, '')
        unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
        
        if file_ext:
            unique_filename = f"{unique_filename.rsplit('.', 1)[0]}.{file_ext}"
        
        # Full file path
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Save file
        file.save(file_path)
        
        # Process image if it's a photo
        if upload_type == 'photo' and mime_type in cls.ALLOWED_IMAGE_TYPES:
            cls._process_image(file_path)
        
        # Return relative path for storage in database
        relative_path = os.path.join(upload_type + 's', unique_filename)
        return relative_path
    
    @classmethod
    def _process_image(cls, image_path):
        """Process uploaded image (resize, optimize)"""
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Resize if too large
                max_size = (800, 800)
                if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Save optimized image
                img.save(image_path, 'JPEG' if image_path.lower().endswith('.jpg') else 'PNG', 
                        optimize=True, quality=85)
        except Exception as e:
            current_app.logger.error(f"Error processing image {image_path}: {str(e)}")
    
    @classmethod
    def get_file_path(cls, relative_path):
        """Get absolute file path from relative path"""
        if not relative_path:
            return None
        
        return os.path.join(current_app.config['UPLOAD_FOLDER'], relative_path)
    
    @classmethod
    def delete_file(cls, relative_path):
        """Delete uploaded file"""
        if not relative_path:
            return False
        
        try:
            file_path = cls.get_file_path(relative_path)
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
        except Exception as e:
            current_app.logger.error(f"Error deleting file {relative_path}: {str(e)}")
        
        return False
    
    @classmethod
    def validate_and_save_photo(cls, file):
        """Validate and save profile photo"""
        is_valid, error, mime_type = cls.validate_file(file, 'image')
        if not is_valid:
            return None, error
        
        try:
            file_path = cls.save_file(file, mime_type, 'photo')
            return file_path, None
        except Exception as e:
            return None, f"Error saving photo: {str(e)}"
    
    @classmethod
    def validate_and_save_resume(cls, file):
        """Validate and save resume"""
        is_valid, error, mime_type = cls.validate_file(file, 'document')
        if not is_valid:
            return None, error
        
        try:
            file_path = cls.save_file(file, mime_type, 'resume')
            return file_path, None
        except Exception as e:
            return None, f"Error saving resume: {str(e)}"