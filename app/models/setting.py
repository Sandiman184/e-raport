from app.core.extensions import db

class Setting(db.Model):
    __tablename__ = 'settings'
    
    key = db.Column(db.String(50), primary_key=True)
    value = db.Column(db.Text)
    
    @staticmethod
    def get_value(key, default=None):
        s = Setting.query.get(key)
        return s.value if s else default
    
    @staticmethod
    def set_value(key, value):
        s = Setting.query.get(key)
        if not s:
            s = Setting(key=key)
            db.session.add(s)
        s.value = value
        db.session.commit()
