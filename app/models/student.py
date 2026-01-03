from app.core.extensions import db

class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    nis = db.Column(db.String(20), unique=True, index=True) # NISM
    nism = db.Column(db.String(20)) # Jika ada NISM vs NIS lokal
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(1), default='L') # L/P
    
    # Metadata tambahan jika diperlukan (Tempat Lahir, Tgl Lahir, dll dari DS)
    active = db.Column(db.Boolean, default=True)
    
    # Relationships
    grades = db.relationship('Grade', backref='student', lazy='dynamic', cascade="all, delete-orphan")
    report_records = db.relationship('ReportRecord', backref='student', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Student {self.name}>'
