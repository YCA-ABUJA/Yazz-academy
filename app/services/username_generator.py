import threading
from datetime import datetime
from app.extensions import db
from app.models.registration_sequence import RegistrationSequence

class UsernameGenerator:
    """Service for generating unique usernames according to YCA format"""
    
    # Role code mapping
    ROLE_CODES = RegistrationSequence.ROLE_CODES
    
    # Program code mapping
    PROGRAM_CODES = RegistrationSequence.PROGRAM_CODES
    
    @staticmethod
    def generate_username(year=None, role_name=None, program_name=None, cohort='A'):
        """
        Generate username in format: YCA/YY/[PROG_CODE]/[ROLE_CODE]/[SEQ4]
        
        Args:
            year: Last two digits of year (24 for 2024). If None, uses current year.
            role_name: Role name (e.g., 'Student', 'Teacher')
            program_name: Program name (e.g., 'Software Engineering')
            cohort: Cohort identifier (default: 'A')
            
        Returns:
            str: Generated username
        """
        if year is None:
            year = datetime.now().year % 100  # Get last two digits
        
        if not role_name:
            raise ValueError("Role name is required")
        
        # Get role code
        role_code = UsernameGenerator.ROLE_CODES.get(role_name)
        if not role_code:
            raise ValueError(f"Invalid role name: {role_name}")
        
        # For non-student roles, program_code might be 'SYS' or other defaults
        if role_name in ['System Admin', 'Head of School', 'Secretary', 'Registrar', 
                        'Financial Secretary', 'Logistic Manager']:
            program_code = 'SYS' if role_name == 'System Admin' else 'ADM'
        else:
            if not program_name:
                raise ValueError(f"Program name is required for {role_name} role")
            
            # Get program code
            program_code = UsernameGenerator.PROGRAM_CODES.get(program_name)
            if not program_code:
                # Generate code from program name if not in mapping
                program_code = ''.join(word[0].upper() for word in program_name.split()[:3])
                if len(program_code) < 2:
                    program_code = program_name[:3].upper()
                program_code = program_code.ljust(3, 'X')[:3]
        
        # Get next sequence with transaction safety
        sequence = RegistrationSequence.get_next_sequence(
            year=year,
            role_code=role_code,
            program_code=program_code,
            cohort=cohort
        )
        
        # Format sequence as 4-digit zero-padded number
        sequence_str = str(sequence).zfill(4)
        
        # Construct username
        username = f"YCA/{year}/{program_code}/{role_code}/{sequence_str}"
        
        return username
    
    @staticmethod
    def batch_generate_usernames(count, role_name, program_name=None, cohort='A'):
        """
        Generate multiple usernames in a batch
        
        Args:
            count: Number of usernames to generate
            role_name: Role name
            program_name: Program name (if applicable)
            cohort: Cohort identifier
            
        Returns:
            list: List of generated usernames
        """
        usernames = []
        year = datetime.now().year % 100
        
        for i in range(count):
            username = UsernameGenerator.generate_username(
                year=year,
                role_name=role_name,
                program_name=program_name,
                cohort=cohort
            )
            usernames.append(username)
        
        return usernames
    
    @staticmethod
    def parse_username(username):
        """
        Parse a YCA username into its components
        
        Args:
            username: YCA username string
            
        Returns:
            dict: Parsed components
        """
        try:
            parts = username.split('/')
            if len(parts) != 5 or parts[0] != 'YCA':
                raise ValueError("Invalid username format")
            
            year = int(parts[1])
            program_code = parts[2]
            role_code = parts[3]
            sequence = int(parts[4])
            
            # Reverse lookup role name
            role_name = next(
                (name for name, code in UsernameGenerator.ROLE_CODES.items() 
                 if code == role_code),
                role_code
            )
            
            # Reverse lookup program name
            program_name = next(
                (name for name, code in UsernameGenerator.PROGRAM_CODES.items() 
                 if code == program_code),
                program_code
            )
            
            return {
                'year': year,
                'program_code': program_code,
                'program_name': program_name,
                'role_code': role_code,
                'role_name': role_name,
                'sequence': sequence,
                'cohort': 'A'  # Default, could be parsed from other data
            }
        except (ValueError, IndexError) as e:
            raise ValueError(f"Failed to parse username '{username}': {str(e)}")