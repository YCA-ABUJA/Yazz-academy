from app.extensions import db
from datetime import datetime

class Program(db.Model):
    """Program/Course model"""
    __tablename__ = 'programs'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic Information
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100), nullable=False)  # Tech & Digital Skills, Communication, etc.
    
    # Duration & Schedule
    duration_weeks = db.Column(db.Integer)
    duration_days = db.Column(db.Integer)  # For short courses
    total_hours = db.Column(db.Integer)
    
    # Pricing
    price_ngn = db.Column(db.Numeric(10, 2), nullable=False)  # Price in NGN
    discount_price = db.Column(db.Numeric(10, 2))
    is_sponsored = db.Column(db.Boolean, default=False)  # e.g., connectED
    
    # Requirements
    prerequisites = db.Column(db.Text)
    learning_outcomes = db.Column(db.JSON, default=list)
    syllabus = db.Column(db.JSON, default=list)  # Store as list of modules/lessons
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    # enrollments = db.relationship('Enrollment', back_populates='program', cascade='all, delete-orphan')
    # cohorts = db.relationship('Cohort', back_populates='program', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Program {self.code}: {self.name}>'
    
    @property
    def display_duration(self):
        """Get formatted duration for display"""
        if self.duration_weeks:
            return f"{self.duration_weeks} weeks"
        elif self.duration_days:
            return f"{self.duration_days} days"
        return "Flexible"
    
    @property
    def display_price(self):
        """Get formatted price for display"""
        if self.is_sponsored:
            return "Sponsored"
        if self.discount_price:
            return f"₦{self.discount_price:,.2f} (₦{self.price_ngn:,.2f})"
        return f"₦{self.price_ngn:,.2f}"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'duration': self.display_duration,
            'price': float(self.price_ngn),
            'display_price': self.display_price,
            'is_sponsored': self.is_sponsored,
            'learning_outcomes': self.learning_outcomes,
            'is_active': self.is_active,
            'is_featured': self.is_featured
        }