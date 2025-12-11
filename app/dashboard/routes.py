from flask import Blueprint, render_template
from flask_login import login_required
from app.decorators import student_required

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    """Main dashboard page"""
    return render_template('dashboard/index.html')

@dashboard_bp.route('/courses')
@login_required
@student_required
def courses():
    """Student courses page"""
    return render_template('dashboard/courses.html')

@dashboard_bp.route('/assignments')
@login_required
@student_required
def assignments():
    """Student assignments page"""
    return render_template('dashboard/assignments.html')

@dashboard_bp.route('/grades')
@login_required
@student_required
def grades():
    """Student grades page"""
    return render_template('dashboard/grades.html')

@dashboard_bp.route('/messages')
@login_required
def messages():
    """Messages page"""
    return render_template('dashboard/messages.html')