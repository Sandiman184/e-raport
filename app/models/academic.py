from app.core.extensions import db
from datetime import datetime

class Subject(db.Model):
    __tablename__ = 'subjects'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True) # Kode Mapel (e.g., MP1)
    name = db.Column(db.String(100), nullable=False) # Al Qur'an, Tajwidz, dll
    kkm = db.Column(db.Float, default=70.0) # KKM Standar
    order = db.Column(db.Integer, default=0) # Urutan cetak di raport
    
    grades = db.relationship('Grade', backref='subject', lazy='dynamic')

class Grade(db.Model):
    __tablename__ = 'grades'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    
    semester = db.Column(db.Integer, nullable=False) # 1 or 2
    year = db.Column(db.String(9), nullable=False) # "2024/2025"
    
    # Poin Penilaian (Scale 0-100)
    nh = db.Column(db.Float, nullable=True) # Nilai Harian
    nk = db.Column(db.Float, nullable=True) # Nilai Keterampilan
    nu = db.Column(db.Float, nullable=True) # Nilai Ujian (UTS/UAS)
    
    # Nilai Akhir (Calculated)
    nr = db.Column(db.Float, nullable=True) # Nilai Raport
    
    # Predikat (A, B, C, D) - Opsi tambahan
    grade_letter = db.Column(db.String(2)) 
    
    __table_args__ = (
        db.UniqueConstraint('student_id', 'subject_id', 'semester', 'year', name='unique_student_grade'),
    )

class ReportRecord(db.Model):
    """
    Menyimpan data non-akademik per semester:
    - Sakit/Ijin/Alpa
    - Catatan Wali Kelas
    - Kepribadian (Akhlak)
    """
    __tablename__ = 'report_records'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    
    semester = db.Column(db.Integer, nullable=False)
    year = db.Column(db.String(9), nullable=False)
    class_name = db.Column(db.String(20)) # Kelas saat itu (e.g., "1 A")
    
    # Kehadiran
    attendance_sakit = db.Column(db.Integer, default=0)
    attendance_izin = db.Column(db.Integer, default=0)
    attendance_alpa = db.Column(db.Integer, default=0)
    
    # Catatan
    notes = db.Column(db.Text) # Catatan Wali Kelas
    
    # Ekstrakurikuler / Kepribadian (Disimpan sebagai JSON Text)
    # Format: [{"name": "Kegiatan", "grade": "A", "desc": "Keterangan"}, ...]
    extra_json = db.Column(db.Text, default='[]')
    
    # Format: [{"aspect": "Kedisiplinan", "grade": "Baik", "desc": "Selalu displin"}, ...]
    personality_json = db.Column(db.Text, default='[]')
    
    personality_rank = db.Column(db.String(50)) # Deprecated/Simple version
    
    # Helper properties
    @property
    def extras(self):
        import json
        if self.extra_json:
            try: return json.loads(self.extra_json)
            except: pass
        return []

    @property
    def personality(self):
        import json
        if self.personality_json:
            try: return json.loads(self.personality_json)
            except: pass
        return []
    
    __table_args__ = (
        db.UniqueConstraint('student_id', 'semester', 'year', name='unique_student_report'),
    )
