from flask import render_template, request, redirect, url_for, flash
from . import students_bp
from app.models import Student
from flask_login import login_required

@students_bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    # Default: Show active students first, then by name
    # Pagination: 20 per page
    pagination = Student.query.order_by(Student.active.desc(), Student.name).paginate(page=page, per_page=20, error_out=False)
    
    # Debug: Check if items exist
    if pagination.total > 0 and not pagination.items and page > 1:
        # If page is empty but total > 0, redirect to page 1
        return redirect(url_for('students.index', page=1))
        
    return render_template('pages/students/index.html', students=pagination)

@students_bp.route('/<int:id>')
@login_required
def detail(id):
    student = Student.query.get_or_404(id)
    return render_template('pages/students/detail.html', student=student)

@students_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    from app.core.extensions import db
    if request.method == 'POST':
        name = request.form.get('name')
        nis = request.form.get('nis')
        gender = request.form.get('gender')
        
        # Simple Validation
        if not name or not nis:
            return render_template('pages/students/form.html', error="Nama dan NIS wajib diisi.")
            
        # Check duplicate
        if Student.query.filter_by(nis=nis).first():
             return render_template('pages/students/form.html', error="NIS sudah terdaftar.")
             
        new_student = Student(name=name, nis=nis, nism=nis, gender=gender, active=True)
        db.session.add(new_student)
        db.session.commit()
        
        return redirect(url_for('students.index'))
        
    return render_template('pages/students/form.html')

@students_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    from app.core.extensions import db
    student = Student.query.get_or_404(id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        nis = request.form.get('nis')
        gender = request.form.get('gender')
        
        # Simple Validation
        if not name or not nis:
            return render_template('pages/students/form.html', student=student, error="Nama dan NIS wajib diisi.")
            
        # Check duplicate if NIS changed
        if nis != student.nis:
            if Student.query.filter_by(nis=nis).first():
                 return render_template('pages/students/form.html', student=student, error="NIS sudah terdaftar.")
        
        student.name = name
        student.nis = nis
        student.nism = nis # Assume NISM follows NIS for now
        student.gender = gender
        
        db.session.commit()
        flash('Data siswa berhasil diperbarui.', 'success')
        
        # Pertahankan context: tetap di halaman edit
        return redirect(url_for('students.edit', id=id))
        
    return render_template('pages/students/form.html', student=student)

@students_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    from app.core.extensions import db
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    return redirect(url_for('students.index'))
