from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from . import grades_bp
from app.models import Subject, Student, Grade
from app.core.extensions import db

@grades_bp.route('/')
@login_required
def index():
    # Selection page
    subjects = Subject.query.order_by(Subject.order, Subject.id).all()
    
    # Check if no subjects exist
    has_subjects = len(subjects) > 0
    
    return render_template('pages/grades/selection.html', subjects=subjects, has_subjects=has_subjects)

@grades_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    subject_id = request.args.get('subject_id', type=int)
    semester = request.args.get('semester', 1, type=int)
    
    if not subject_id:
        return redirect(url_for('grades.index'))
    
    subject = Subject.query.get_or_404(subject_id)
    students = Student.query.order_by(Student.name).all()
    
    if request.method == 'POST':
        # Handle Batch Update
        try:
            from app.models.setting import Setting
            current_year = Setting.get_value('academic_year', '2024/2025')
            
            count_updated = 0
            for student in students:
                prefix = f"s_{student.id}_"
                
                # Get inputs
                nh = request.form.get(f"{prefix}nh")
                nk = request.form.get(f"{prefix}nk")
                nu = request.form.get(f"{prefix}nu")
                
                # Validation / Cleaning
                def clean_val(v):
                    if not v or v.strip() == '': return None
                    return float(v)
                
                nh_val = clean_val(nh)
                nk_val = clean_val(nk)
                nu_val = clean_val(nu)
                
                # Calculate NR (Example Logic: Average if incomplete, or custom)
                # Excel Logic seems to be: If incomplete, avg. If complete, weighted.
                # Let's simple Avg for now
                vals = [v for v in [nh_val, nk_val, nu_val] if v is not None]
                nr_val = sum(vals) / len(vals) if vals else None
                
                # Save
                g = Grade.query.filter_by(
                    student_id=student.id,
                    subject_id=subject.id,
                    semester=semester,
                    year=current_year
                ).first()
                
                if not g:
                    g = Grade(student_id=student.id, subject_id=subject.id, semester=semester, year=current_year)
                    db.session.add(g)
                
                g.nh = nh_val
                g.nk = nk_val
                g.nu = nu_val
                g.nr = nr_val
                
                count_updated += 1
            
            db.session.commit()
            flash(f'Nilai berhasil disimpan ({count_updated} siswa).')
            return redirect(url_for('grades.edit', subject_id=subject_id, semester=semester))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Gagal menyimpan: {str(e)}')
    
    # Pre-fetch existing grades for display
    # Dict mapping student_id -> GradeObj
    from app.models.setting import Setting
    current_year = Setting.get_value('academic_year', '2024/2025')
    existing_grades = {}
    grades_q = Grade.query.filter_by(subject_id=subject.id, semester=semester, year=current_year).all()
    for g in grades_q:
        existing_grades[g.student_id] = g
    
    return render_template('pages/grades/edit.html', subject=subject, students=students, existing_grades=existing_grades, semester=semester)

@grades_bp.route('/extras', methods=['GET', 'POST'])
@login_required
def extras():
    # List all students to pick one to edit extras
    
    students = Student.query.order_by(Student.name).all()
    
    if request.method == 'POST':
        try:
            # Batch update simplified: Just Attendance & Notes for now
            count = 0
            for s in students:
                prefix = f"s_{s.id}_"
                sakit = request.form.get(f"{prefix}sakit")
                izin = request.form.get(f"{prefix}izin")
                alpa = request.form.get(f"{prefix}alpa")
                notes = request.form.get(f"{prefix}notes")
                
                # Retrieve or Create Record
                
                from app.models import ReportRecord
                rr = ReportRecord.query.filter_by(
                    student_id=s.id, semester=1, year='2024/2025'
                ).first()
                
                if not rr:
                    rr = ReportRecord(student_id=s.id, semester=1, year='2024/2025')
                    # Defaults for JSON
                    rr.extra_json = '[{"name": "Muhadloroh", "grade": "B", "desc": "Baik"}, {"name": "Sholat Berjamaah", "grade": "A", "desc": "Sangat Baik"}]'
                    rr.personality_json = '[{"aspect": "Kedisiplinan", "grade": "Baik", "desc": "Tertib"}, {"aspect": "Kebersihan", "grade": "Baik", "desc": "Rapi"}]'
                    db.session.add(rr)
                
                if sakit: rr.attendance_sakit = int(sakit)
                if izin: rr.attendance_izin = int(izin)
                if alpa: rr.attendance_alpa = int(alpa)
                if notes: rr.notes = notes
                
                count += 1
            
            db.session.commit()
            flash('Data kehadiran & catatan berhasil disimpan.')
            return redirect(url_for('grades.extras'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {e}')
            
    # Fetch existing data to populate form
    from app.models import ReportRecord
    from app.models.setting import Setting
    current_year = Setting.get_value('academic_year', '2024/2025')
    records = {r.student_id: r for r in ReportRecord.query.filter_by(semester=1, year=current_year).all()}
    
    return render_template('pages/grades/extras.html', students=students, records=records)
