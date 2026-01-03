from flask import render_template, request, flash, redirect, url_for, send_file, current_app
from flask_login import login_required, current_user
from . import settings_bp
from app.models import Setting, Grade, ReportRecord
from app.core.extensions import db
from sqlalchemy import text
from app.services.backup_service import BackupService
from app.services.import_service import ImportService
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

    # Prepare common data
    backups = BackupService.get_backups()
    years = []
    try:
        grade_years = db.session.query(Grade.year).distinct().all()
        report_years = db.session.query(ReportRecord.year).distinct().all()
        all_years = set([y[0] for y in grade_years] + [y[0] for y in report_years])
        years = sorted(list(all_years), reverse=True)
    except: pass

    impact_data = None
    estimates = BackupService.get_backup_estimates()

    if request.method == 'POST':
        # Handle Backup Actions
        action = request.form.get('action')
        
        if action == 'analyze_prune':
            year = request.form.get('prune_year')
            if not year:
                flash('Pilih tahun ajaran terlebih dahulu.', 'error')
            else:
                impact_data = BackupService.analyze_prune_impact(year)
                # Don't redirect, just fall through to render with impact_data
        
        elif action == 'backup':
            try:
                desc = request.form.get('backup_desc')
                scope = request.form.get('backup_scope', 'full')
                year_filter = None
                
                if scope == 'year':
                    year_filter = request.form.get('backup_year')
                    if not year_filter:
                         flash('Pilih tahun ajaran untuk backup.', 'error')
                         return redirect(url_for('settings.index'))

                BackupService.create_backup(description=desc, year_filter=year_filter)
                flash('Backup berhasil dibuat dan disimpan di server.', 'success')
                return redirect(url_for('settings.index'))
            except Exception as e:
                flash(f'Gagal membuat backup: {str(e)}', 'error')
        
        elif action == 'reset_data':
            confirm = request.form.get('confirm_reset', '').strip()
            if confirm != 'RESET DATA':
                flash('Konfirmasi reset tidak valid. Ketik "RESET DATA" dengan tepat.', 'error')
            else:
                try:
                    # Auto Backup
                    BackupService.create_backup(description="AutoBackup_BeforeReset")
                    user_id = current_user.id if current_user.is_authenticated else None
                    success, msg = BackupService.reset_academic_data(user_id=user_id)
                    if success:
                        flash(msg, 'success')
                    else:
                        flash(msg, 'warning')
                except Exception as e:
                    flash(f'Gagal reset data: {str(e)}', 'error')
            return redirect(url_for('settings.index'))

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
                user_id = current_user.id if current_user.is_authenticated else None
                BackupService.restore_from_local(filename, user_id=user_id)
                flash('Database berhasil dipulihkan dari backup server. Silakan refresh.', 'success')
                return redirect(url_for('settings.index'))
            except Exception as e:
                flash(f'Gagal restore: {str(e)}', 'error')

        elif action == 'delete_backup':
            filename = request.form.get('filename')
            try:
                if BackupService.delete_backup(filename):
                    flash('File backup berhasil dihapus.', 'success')
                else:
                    flash('File tidak ditemukan.', 'error')
                return redirect(url_for('settings.index'))
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
                        return redirect(url_for('settings.index'))
                    except Exception as e:
                        flash(f'Gagal restore: {str(e)}', 'error')

        elif action == 'prune':
            year = request.form.get('prune_year')
            confirm = request.form.get('confirm_prune', '').strip().upper()
            
            if not year:
                flash('Pilih tahun ajaran terlebih dahulu.', 'error')
            elif confirm != 'YES':
                flash('Konfirmasi penghapusan tidak valid. Harap ketik "YES".', 'error')
            else:
                try:
                    # Auto backup before prune
                    BackupService.create_backup(description=f"AutoBackup_BeforePrune_{year.replace('/', '-')}")
                    
                    user_id = current_user.id if current_user.is_authenticated else None
                    success, msg = BackupService.prune_year(year, user_id=user_id)
                    if success:
                        flash(msg, 'success')
                    else:
                        flash(msg, 'warning')
                    return redirect(url_for('settings.index'))
                except Exception as e:
                    flash(f'Gagal menghapus data: {str(e)}', 'error')

        elif action == 'import_students':
            if 'import_file' not in request.files:
                flash('Tidak ada file yang dipilih', 'error')
            else:
                file = request.files['import_file']
                if file.filename == '':
                    flash('Tidak ada file yang dipilih', 'error')
                else:
                    success, msg = ImportService.import_students(file)
                    if success:
                        flash(msg, 'success')
                    else:
                        flash(msg, 'error')
                    return redirect(url_for('settings.index'))

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
    
    # If not POST or if fall through (analyze_prune), render template
    return render_template('pages/settings/index.html', Setting=Setting, backups=backups, years=years, impact_data=impact_data, estimates=estimates)

