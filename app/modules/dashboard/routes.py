from flask import render_template
from flask_login import login_required
from . import dashboard_bp

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    from app.models import Student, Subject, Grade
    from app.core.extensions import db
    
    student_count = Student.query.count()
    subject_count = Subject.query.count()
    # Unique classes logic (Approximation based on grade level or manually set groups?)
    # For now, placeholder or derived
    class_count = 1 # Single class for now
    
    return render_template('pages/dashboard/index.html', 
                           student_count=student_count,
                           subject_count=subject_count,
                           class_count=class_count)
