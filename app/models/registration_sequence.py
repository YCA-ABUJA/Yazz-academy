from app.extensions import db
from datetime import datetime
from sqlalchemy import UniqueConstraint

class RegistrationSequence(db.Model):
    """Track registration sequences for username generation"""
    __tablename__ = 'registration_sequences'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Sequence key components
    year = db.Column(db.Integer, nullable=False)  # Last two digits of year, e.g., 24 for 2024
    role_code = db.Column(db.String(10), nullable=False)  # Role code: SYS, HOS, SEC, REG, FIN, LOG, TCH, STD
    program_code = db.Column(db.String(10), nullable=False)  # Program code: SE, WD, DA, CY, etc.
    cohort = db.Column(db.String(10), nullable=False, default='A')  # Cohort identifier
    
    # Sequence value
    current_sequence = db.Column(db.Integer, nullable=False, default=0)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint
    __table_args__ = (
        UniqueConstraint('year', 'role_code', 'program_code', 'cohort', 
                        name='unique_sequence_key'),
    )
    
    # Role codes mapping
    ROLE_CODES = {
        'System Admin': 'SYS',
        'Head of School': 'HOS',
        'Secretary': 'SEC',
        'Registrar': 'REG',
        'Financial Secretary': 'FIN',
        'Logistic Manager': 'LOG',
        'Teacher': 'TCH',
        'Student': 'STD',
        'Guest': 'GST'
    }
    
    # Program codes mapping (from catalogue)
    PROGRAM_CODES = {
        'Python Programming': 'PYT',
        'Web Development': 'WD',
        'Creative Coding': 'CC',
        'Cybersecurity Fundamentals': 'CYF',
        'Data Analytics': 'DA',
        'Public Speaking': 'PS',
        'Speech Writing': 'SW',
        'Storytelling': 'ST',
        'Scratch 3.0': 'SC3',
        'Canva': 'CV',
        'Google Classroom': 'GC',
        'Summer Camp': 'SC',
        'connectED': 'CED',
        'Cybersecurity Mythology Series': 'CMS'
    }
    
    def __repr__(self):
        return f'<RegistrationSequence {self.year}/{self.role_code}/{self.program_code}/{self.cohort}: {self.current_sequence}>'
    
    @classmethod
    def get_next_sequence(cls, year, role_code, program_code, cohort='A'):
        """Get next sequence number with row locking for concurrency safety"""
        from sqlalchemy import func
        
        # Start transaction with row locking
        sequence = cls.query.filter_by(
            year=year,
            role_code=role_code,
            program_code=program_code,
            cohort=cohort
        ).with_for_update().first()
        
        if not sequence:
            # Create new sequence if doesn't exist
            sequence = cls(
                year=year,
                role_code=role_code,
                program_code=program_code,
                cohort=cohort,
                current_sequence=0
            )
            db.session.add(sequence)
        
        # Increment and return
        sequence.current_sequence += 1
        db.session.commit()
        
        return sequence.current_sequence