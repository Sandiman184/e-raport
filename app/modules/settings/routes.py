from flask import render_template, request, flash, redirect, url_for, send_file, current_app
from flask_login import login_required
from . import settings_bp
from app.models import Setting, Grade, ReportRecord
from app.core.extensions import db
from sqlalchemy import text
from app.services.backup_service import BackupService
import os

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
        # Handle Backup Actions
        action = request.form.get('action')
        
        if action == 'backup':
            try:
                desc = request.form.get('backup_desc')
                BackupService.create_backup(description=desc)
                flash('Backup berhasil dibuat dan disimpan di server.', 'success')
            except Exception as e:
                flash(f'Gagal membuat backup: {str(e)}', 'error')
        
        elif action == 'download_backup':
            try:
                filename = request.form.get('filename')
                backup_dir = os.path.join(current_app.root_path, '..', 'storage', 'backups')
                path = os.path.join(backup_dir, filename)
                if os.path.exists(path):
                    return send_file(path, as_attachment=True, download_name=filename)
                flash('File tidak ditemukan', 'error')
            except Exception as e:
                flash(f'Error: {str(e)}', 'error')

        elif action == 'restore_local':
            filename = request.form.get('filename')
            try:
                BackupService.restore_from_local(filename)
                flash('Database berhasil dipulihkan dari backup server. Silakan refresh.', 'success')
            except Exception as e:
                flash(f'Gagal restore: {str(e)}', 'error')

        elif action == 'delete_backup':
            filename = request.form.get('filename')
            try:
                if BackupService.delete_backup(filename):
                    flash('File backup berhasil dihapus.', 'success')
                else:
                    flash('File tidak ditemukan.', 'error')
            except Exception as e:
                flash(f'Gagal menghapus: {str(e)}', 'error')
        
        elif action == 'restore':
            if 'backup_file' not in request.files:
                flash('Tidak ada file yang dipilih', 'error')
            else:
                file = request.files['backup_file']
                if file.filename == '':
                    flash('Tidak ada file yang dipilih', 'error')
                else:
                    try:
                        BackupService.restore_backup(file)
                        flash('Database berhasil dipulihkan. Silakan refresh halaman.', 'success')
                    except Exception as e:
                        flash(f'Gagal restore: {str(e)}', 'error')

        elif action == 'prune':
            year = request.form.get('prune_year')
            confirm = request.form.get('confirm_prune')
            
            if not year:
                flash('Pilih tahun ajaran terlebih dahulu.', 'error')
            elif confirm != 'YES':
                flash('Konfirmasi penghapusan tidak valid.', 'error')
            else:
                try:
                    # Auto backup before prune
                    BackupService.create_backup(description=f"AutoBackup_BeforePrune_{year.replace('/', '-')}")
                    
                    success, msg = BackupService.prune_year(year)
                    if success:
                        flash(msg, 'success')
                    else:
                        flash(msg, 'warning')
                except Exception as e:
                    flash(f'Gagal menghapus data: {str(e)}', 'error')

        else:
            # Normal Settings Save
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
                
            flash('Pengaturan berhasil disimpan.', 'success')
            return redirect(url_for('settings.index'))
    
    backups = BackupService.get_backups()
    
    # Get distinct years for prune dropdown
    years = []
    try:
        # Fetch distinct years from Grade and ReportRecord
        grade_years = db.session.query(Grade.year).distinct().all()
        report_years = db.session.query(ReportRecord.year).distinct().all()
        
        # Combine and unique
        all_years = set([y[0] for y in grade_years] + [y[0] for y in report_years])
        years = sorted(list(all_years), reverse=True)
    except:
        pass

    return render_template('pages/settings/index.html', Setting=Setting, backups=backups, years=years)
