from flask import render_template, make_response, request
from flask_login import login_required
from . import reports_bp
from app.models import Student, Subject, Grade, ReportRecord

@reports_bp.route('/')
@login_required
def index():
    # List student to print with Pagination
    page = request.args.get('page', 1, type=int)
    students = Student.query.order_by(Student.name).paginate(page=page, per_page=12, error_out=False)
    return render_template('pages/reports/index.html', students=students)

# IMPORTANT: Route name should match url_for('reports.print_report')
@reports_bp.route('/<int:student_id>/print')
@login_required
def print_report(student_id):
    semester = request.args.get('semester', 1, type=int)
    student = Student.query.get_or_404(student_id)
    
    # Get all subjects
    subjects = Subject.query.order_by(Subject.order, Subject.id).all()
    
    # Get Grades
    grades_q = Grade.query.filter_by(student_id=student_id, semester=semester, year='2024/2025').all()
    grades = {g.subject_id: g for g in grades_q}
        
    # Extra Records (Attendance, Notes, JSONs)
    rr = ReportRecord.query.filter_by(student_id=student_id, semester=semester, year='2024/2025').first()
    
    # Default empty structure if not found
    record = rr if rr else ReportRecord(
        attendance_sakit=0, attendance_izin=0, attendance_alpa=0, 
        notes="-", extra_json='[]', personality_json='[]'
    )
    
    return render_template('pages/reports/print_template.html', 
                           student=student,
                           subjects=subjects,
                           grades=grades,
                           semester=semester,
                           record=record)
