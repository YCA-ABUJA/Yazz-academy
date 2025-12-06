from flask import Blueprint, render_template

marketing_bp = Blueprint('marketing', __name__)

@marketing_bp.route('/')
def index():
    """Home page"""
    return render_template('marketing/index.html')

@marketing_bp.route('/about')
def about():
    """About page"""
    return render_template('marketing/about.html')

@marketing_bp.route('/courses')
def courses():
    """Courses catalog"""
    return render_template('marketing/courses.html')

@marketing_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page"""
    return render_template('marketing/contact.html')