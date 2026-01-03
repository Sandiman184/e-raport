import os
import shutil
import sqlite3
from datetime import datetime
from flask import current_app, send_file
from werkzeug.utils import secure_filename
from app.core.extensions import db

class BackupService:
    @staticmethod
    def get_db_path():
        """Helper to get the current SQLite database path from config"""
        # Parse URI like 'sqlite:///path/to/db.sqlite'
        uri = current_app.config['SQLALCHEMY_DATABASE_URI']
        if uri.startswith('sqlite:///'):
            path = uri.replace('sqlite:///', '')
            # Handle relative paths if necessary (though usually absolute in config)
            if not os.path.isabs(path):
                path = os.path.join(current_app.root_path, '..', path)
            return os.path.abspath(path)
        return None

    @staticmethod
    def verify_integrity(db_path):
        """Verifies SQLite database integrity"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check;")
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0] == 'ok':
                return True, "Integrity check passed"
            return False, f"Integrity check failed: {result[0] if result else 'Unknown error'}"
        except Exception as e:
            return False, f"Integrity check error: {str(e)}"

    @staticmethod
    def get_backups():
        """Returns list of available backups"""
        backup_dir = os.path.join(current_app.root_path, '..', 'storage', 'backups')
        if not os.path.exists(backup_dir):
            return []
            
        backups = []
        for f in os.listdir(backup_dir):
            if f.endswith('.sqlite'):
                path = os.path.join(backup_dir, f)
                stat = os.stat(path)
                backups.append({
                    'filename': f,
                    'size': stat.st_size,
                    'created_at': datetime.fromtimestamp(stat.st_ctime),
                    'path': path
                })
        
        # Sort by creation time desc
        return sorted(backups, key=lambda x: x['created_at'], reverse=True)

    @staticmethod
    def restore_from_local(filename, user_id=None):
        """Restores from a local backup file"""
        from app.models import AuditLog
        backup_dir = os.path.join(current_app.root_path, '..', 'storage', 'backups')
        source_path = os.path.join(backup_dir, secure_filename(filename))
        
        if not os.path.exists(source_path):
            raise Exception("Backup file not found")
            
        # Verify integrity
        valid, msg = BackupService.verify_integrity(source_path)
        if not valid:
            raise Exception(f"Backup file is corrupt: {msg}")

        db_path = BackupService.get_db_path()
        
        # Create safety backup
        try:
            BackupService.create_backup(description="SafetyBackup_BeforeRestoreLocal")
        except: pass
        
        # Restore
        try:
            shutil.copy2(source_path, db_path)
            
            # Log
            if user_id: # Need context to write log after restore? 
                # After restore, the DB is replaced. So we write log to NEW DB.
                # But connection might need refresh.
                # However, AuditLog table should exist in backup if backup is recent.
                # If backup is old (before AuditLog), this might fail.
                # Let's assume schema is migrated or we catch error.
                pass 
                
            return True
        except Exception as e:
            raise e

    @staticmethod
    def delete_backup(filename):
        """Deletes a local backup file"""
        backup_dir = os.path.join(current_app.root_path, '..', 'storage', 'backups')
        file_path = os.path.join(backup_dir, secure_filename(filename))
        
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    
    @staticmethod
    def get_backup_estimates():
        """Returns estimates for backup sizes and durations."""
        db_path = BackupService.get_db_path()
        if not db_path or not os.path.exists(db_path):
            return {}

        total_size = os.path.getsize(db_path)
        # Estimate duration: assume 10MB/s copy speed
        # Min 1 second
        total_duration_sec = total_size / (10 * 1024 * 1024) 
        if total_duration_sec < 1: total_duration_sec = 1

        estimates = {
            'full': {
                'size_bytes': total_size,
                'size_fmt': f"{total_size / 1024 / 1024:.2f} MB",
                'duration_sec': round(total_duration_sec, 2)
            },
            'years': {}
        }
        
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            
            # Get distinct years from grades to estimate partial sizes
            # This is a rough estimate based on grade distribution
            cur.execute("SELECT COUNT(*) FROM grades")
            res = cur.fetchone()
            total_grades = res[0] if res else 0
            
            if total_grades > 0:
                cur.execute("SELECT year, COUNT(*) FROM grades GROUP BY year")
                rows = cur.fetchall()
                for year, count in rows:
                    if not year: continue
                    ratio = count / total_grades
                    # Base overhead + proportional data
                    est_size = (total_size * 0.1) + (total_size * 0.9 * ratio)
                    est_dur = est_size / (10 * 1024 * 1024)
                    if est_dur < 1: est_dur = 1
                    
                    estimates['years'][year] = {
                        'size_bytes': int(est_size),
                        'size_fmt': f"{est_size / 1024 / 1024:.2f} MB",
                        'duration_sec': round(est_dur, 2)
                    }
            conn.close()
        except Exception as e:
            print(f"Error estimating backup: {e}")
            pass
            
        return estimates

    @staticmethod
    def create_backup(description=None, year_filter=None):
        """
        Creates a copy of the SQLite database file.
        If year_filter is provided, creates a partial backup containing only data for that year.
        """
        db_path = BackupService.get_db_path()
        if not db_path or not os.path.exists(db_path):
            raise Exception("Database file not found")

        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        desc_part = f"_{secure_filename(description)}" if description else ""
        year_part = f"_Year-{secure_filename(year_filter.replace('/', '-'))}" if year_filter else ""
        
        backup_filename = f"backup_eraport_{timestamp}{year_part}{desc_part}.sqlite"
        backup_dir = os.path.join(current_app.root_path, '..', 'storage', 'backups')
        
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
            
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # 1. Copy full DB first (as temp if filtering, or final if not)
        temp_path = backup_path + ".temp"
        shutil.copy2(db_path, temp_path)
        
        try:
            if year_filter:
                # 2. Open temp DB and prune other years
                conn = sqlite3.connect(temp_path)
                cur = conn.cursor()
                
                # Delete Grades not in year
                cur.execute("DELETE FROM grades WHERE year != ?", (year_filter,))
                # Delete ReportRecords not in year
                cur.execute("DELETE FROM report_records WHERE year != ?", (year_filter,))
                
                # We do NOT delete Students/Subjects as they are master data needed for the records
                
                conn.commit()
                cur.execute("VACUUM") # Reclaim space
                conn.close()
            
            # 3. Finalize
            if os.path.exists(backup_path):
                os.remove(backup_path)
            os.rename(temp_path, backup_path)
            
            # Verify integrity
            valid, msg = BackupService.verify_integrity(backup_path)
            if not valid:
                if os.path.exists(backup_path):
                    os.remove(backup_path)
                raise Exception(f"Backup created but failed integrity check: {msg}")
                
            return backup_path
            
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            if os.path.exists(backup_path):
                os.remove(backup_path)
            raise e

    @staticmethod
    def restore_backup(file_storage):
        """Restores database from an uploaded file"""
        db_path = BackupService.get_db_path()
        if not db_path:
            raise Exception("Database configuration error")

        # Create a safety backup before overwriting
        try:
            BackupService.create_backup(description="SafetyBackup_BeforeRestore")
        except:
            pass # Proceed even if auto-backup fails, but ideally log it

        # Save uploaded file temporarily
        temp_path = db_path + ".restore_temp"
        file_storage.save(temp_path)

        # Verify integrity
        valid, msg = BackupService.verify_integrity(temp_path)
        if not valid:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise Exception(f"Invalid backup file: {msg}")

        # Verify it's a valid SQLite file and has tables
        try:
            conn = sqlite3.connect(temp_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            conn.close()
            
            if not tables:
                os.remove(temp_path)
                raise Exception("Invalid or empty database file (no tables found)")
                
            # Replace current DB
            # Windows might lock the file if app is running, but Flask dev server usually allows it.
            # Production with Gunicorn might need a restart.
            shutil.move(temp_path, db_path)
            return True
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise e

    @staticmethod
    def analyze_prune_impact(year):
        """
        Analyzes the impact of pruning a specific academic year.
        Returns a dict with counts and risk assessment.
        """
        from app.models import Grade, ReportRecord
        
        year = str(year).strip()
        impact = {
            'year': year,
            'grades_count': 0,
            'reports_count': 0,
            'total_records': 0,
            'risk_level': 'LOW',
            'details': []
        }
        
        if not year:
            return impact
            
        grades_count = Grade.query.filter_by(year=year).count()
        reports_count = ReportRecord.query.filter_by(year=year).count()
        
        impact['grades_count'] = grades_count
        impact['reports_count'] = reports_count
        impact['total_records'] = grades_count + reports_count
        
        if impact['total_records'] > 0:
            impact['risk_level'] = 'HIGH' # Destructive operation is always high risk
            impact['details'].append(f"Akan menghapus {grades_count} data nilai santri.")
            impact['details'].append(f"Akan menghapus {reports_count} arsip laporan.")
        else:
            impact['details'].append("Tidak ada data yang ditemukan untuk tahun ini.")
            
        return impact

    @staticmethod
    def prune_year(year, user_id=None):
        """
        Deletes data for a specific academic year.
        WARNING: This is destructive.
        Targets: Grade, ReportRecord
        """
        from app.models import Grade, ReportRecord, AuditLog
        
        try:
            year = str(year).strip()
            if not year:
                return False, "Tahun ajaran tidak valid (kosong)."

            # 1. Count records to be deleted
            grades_count = Grade.query.filter_by(year=year).count()
            reports_count = ReportRecord.query.filter_by(year=year).count()
            
            if grades_count == 0 and reports_count == 0:
                return False, f"Tidak ada data ditemukan untuk tahun ajaran '{year}'. Pastikan format tahun sesuai."

            # 2. Delete
            Grade.query.filter_by(year=year).delete()
            ReportRecord.query.filter_by(year=year).delete()
            
            # 3. Audit Log
            log_details = f"Deleted {grades_count} grades and {reports_count} reports for year {year}"
            audit = AuditLog(
                user_id=user_id,
                action='PRUNE_YEAR',
                target=f"Year {year}",
                details=log_details,
                status='SUCCESS'
            )
            db.session.add(audit)
            
            db.session.commit()
            
            return True, f"Berhasil menghapus {grades_count} nilai dan {reports_count} laporan untuk tahun {year}."
        except Exception as e:
            db.session.rollback()
            # Log Failure if possible
            try:
                audit = AuditLog(
                    user_id=user_id,
                    action='PRUNE_YEAR',
                    target=f"Year {year}",
                    details=f"Error: {str(e)}",
                    status='FAILED'
                )
                db.session.add(audit)
                db.session.commit()
            except: pass
            raise e

    @staticmethod
    def reset_academic_data(user_id=None):
        """
        Deletes ALL academic data: Students, Grades, ReportRecords.
        Keeps: Users, Settings, Subjects.
        """
        from app.models import Student, Grade, ReportRecord, AuditLog
        
        try:
            # 1. Count
            s_count = Student.query.count()
            g_count = Grade.query.count()
            r_count = ReportRecord.query.count()
            
            if s_count == 0 and g_count == 0 and r_count == 0:
                return False, "Data sudah kosong."

            # 2. Delete
            # Cascade should handle Grades/Reports if Student is deleted, but explicit is safer/clearer
            Grade.query.delete()
            ReportRecord.query.delete()
            Student.query.delete()
            
            # 3. Log
            audit = AuditLog(
                user_id=user_id,
                action='RESET_DATA',
                target='ALL_ACADEMIC_DATA',
                details=f"Deleted {s_count} students, {g_count} grades, {r_count} reports.",
                status='SUCCESS'
            )
            db.session.add(audit)
            db.session.commit()
            return True, f"Reset berhasil. {s_count} siswa, {g_count} nilai, {r_count} laporan dihapus."
        except Exception as e:
            db.session.rollback()
            try:
                 audit = AuditLog(
                    user_id=user_id,
                    action='RESET_DATA',
                    target='ALL_ACADEMIC_DATA',
                    details=f"Error: {str(e)}",
                    status='FAILED'
                )
                 db.session.add(audit)
                 db.session.commit()
            except: pass
            raise e
