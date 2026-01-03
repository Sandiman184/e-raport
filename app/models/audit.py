
from app.core.extensions import db
from datetime import datetime

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) # Nullable if system action
    action = db.Column(db.String(50), nullable=False) # e.g., 'PRUNE_DATA', 'RESTORE_BACKUP'
    target = db.Column(db.String(100), nullable=True) # e.g., 'Year 2024/2025'
    details = db.Column(db.Text, nullable=True) # JSON or Text description
    ip_address = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(20), default='SUCCESS') # SUCCESS, FAILED
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref='logs')

    def __repr__(self):
        return f"<AuditLog {self.action} by {self.user_id} at {self.timestamp}>"
