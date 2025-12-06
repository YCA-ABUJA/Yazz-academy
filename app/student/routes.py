from flask import Blueprint, render_template
from flask_login import login_required
from app.decorators import student_required

student_bp = Blueprint('student', __name__)

@student_bp.route('/')
@login_required
@student_required
def dashboard():
    """Student dashboard"""
    return render_template('student/dashboard.html')