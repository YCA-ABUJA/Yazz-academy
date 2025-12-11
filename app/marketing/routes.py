from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from app.extensions import mail
from flask_mail import Message
from app.models.program import Program

marketing_bp = Blueprint('marketing', __name__)

@marketing_bp.route('/')
def index():
    """Home page"""
    # Get featured programs from database
    featured_programs = Program.query.filter_by(is_featured=True).limit(6).all()
    return render_template('marketing/index.html', featured_programs=featured_programs)

@marketing_bp.route('/about')
def about():
    """About page"""
    return render_template('marketing/about.html')

@marketing_bp.route('/courses')
def courses():
    """Courses catalog"""
    programs = Program.query.filter_by(is_active=True).all()
    return render_template('marketing/courses.html', programs=programs)

@marketing_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page"""
    if request.method == 'POST':
        return contact_submit()
    return render_template('marketing/contact.html')

@marketing_bp.route('/contact/submit', methods=['POST'])
def contact_submit():
    """Handle contact form submission"""
    try:
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        
        # Send email
        msg = Message(
            subject=f'New Contact Form Submission from {name}',
            recipients=['services@yca-abuja.com'],
            reply_to=email,
            body=f"""
            Name: {name}
            Email: {email}
            Message: {message}
            """
        )
        mail.send(msg)
        
        flash('Thank you for your message! We will get back to you within 24 hours.', 'success')
        return jsonify({'success': True, 'message': 'Message sent successfully!'})
        
    except Exception as e:
        flash('There was an error sending your message. Please try again.', 'danger')
        return jsonify({'success': False, 'message': str(e)}), 500

@marketing_bp.route('/blog')
def blog():
    """Blog page"""
    return render_template('marketing/blog.html')

@marketing_bp.route('/faq')
def faq():
    """FAQ page"""
    return render_template('marketing/faq.html')

@marketing_bp.route('/announcements')
def announcements():
    """Announcements page"""
    return render_template('marketing/announcements.html')