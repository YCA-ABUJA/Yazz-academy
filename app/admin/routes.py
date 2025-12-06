from flask import Blueprint, render_template
from flask_login import login_required
from app.decorators import admin_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    """Admin dashboard"""
    return render_template('admin/dashboard.html')

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """User management"""
    return render_template('admin/users.html')

@admin_bp.route('/programs')
@login_required
@admin_required
def programs():
    """Program management"""
    return render_template('admin/programs.html')