from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required
from . import settings_bp
from app.models import Setting
from app.core.extensions import db
from sqlalchemy import text

@settings_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    # Ensure table exists (Lazy migration)
    try:
        Setting.query.first()
    except:
        try:
            with db.session.begin():
                db.session.execute(text("CREATE TABLE IF NOT EXISTS settings (key VARCHAR(50) PRIMARY KEY, value TEXT)"))
        except: pass

    if request.method == 'POST':
        # List of keys to save
        keys = [
            'school_name', 'school_address', 'school_nsdt', 'school_district_city', # KOP
            'headmaster_name', 'headmaster_nip', # TTD Kepsek
            'report_place', 'report_date', # Titi Mangsa
            'academic_year', # Tahun Ajaran
            'class_name_default' # Kelas Default
        ]
        
        for k in keys:
            val = request.form.get(k, '')
            Setting.set_value(k, val)
            
        flash('Pengaturan berhasil disimpan.')
        return redirect(url_for('settings.index'))
    
    return render_template('pages/settings/index.html', Setting=Setting)
