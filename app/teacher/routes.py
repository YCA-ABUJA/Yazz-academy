from flask import Blueprint, render_template
from flask_login import login_required
from app.decorators import teacher_required

teacher_bp = Blueprint('teacher', __name__)

@teacher_bp.route('/')
@login_required
@teacher_required
def dashboard():
    """Teacher dashboard"""
    return render_template('teacher/dashboard.html')