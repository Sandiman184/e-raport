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
    def restore_from_local(filename):
        """Restores from a local backup file"""
        backup_dir = os.path.join(current_app.root_path, '..', 'storage', 'backups')
        source_path = os.path.join(backup_dir, secure_filename(filename))
        
        if not os.path.exists(source_path):
            raise Exception("Backup file not found")
            
        db_path = BackupService.get_db_path()
        
        # Create safety backup
        try:
            BackupService.create_backup()
        except: pass
        
        # Restore
        shutil.copy2(source_path, db_path)
        return True

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
    def create_backup(description=None):
        """Creates a copy of the SQLite database file with optional description"""
        db_path = BackupService.get_db_path()
        if not db_path or not os.path.exists(db_path):
            raise Exception("Database file not found")

        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        desc_slug = f"_{secure_filename(description)}" if description else ""
        backup_filename = f"backup_eraport_{timestamp}{desc_slug}.sqlite"
        backup_dir = os.path.join(current_app.root_path, '..', 'storage', 'backups')
        
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
            
        backup_path = os.path.join(backup_dir, backup_filename)
        shutil.copy2(db_path, backup_path)
        
        return backup_path

    @staticmethod
    def restore_backup(file_storage):
        """Restores database from an uploaded file"""
        db_path = BackupService.get_db_path()
        if not db_path:
            raise Exception("Database configuration error")

        # Create a safety backup before overwriting
        try:
            BackupService.create_backup()
        except:
            pass # Proceed even if auto-backup fails, but ideally log it

        # Save uploaded file temporarily
        temp_path = db_path + ".restore_temp"
        file_storage.save(temp_path)

        # Verify it's a valid SQLite file
        try:
            conn = sqlite3.connect(temp_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            conn.close()
            
            if not tables:
                os.remove(temp_path)
                raise Exception("Invalid or empty database file")
                
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
    def prune_year(year):
        """
        Deletes data for a specific academic year.
        WARNING: This is destructive.
        Targets: Grade, ReportRecord
        """
        from app.models import Grade, ReportRecord
        
        try:
            # 1. Count records to be deleted
            grades_count = Grade.query.filter_by(year=year).count()
            reports_count = ReportRecord.query.filter_by(year=year).count()
            
            if grades_count == 0 and reports_count == 0:
                return False, "Tidak ada data untuk tahun ajaran tersebut."

            # 2. Delete
            Grade.query.filter_by(year=year).delete()
            ReportRecord.query.filter_by(year=year).delete()
            
            db.session.commit()
            
            return True, f"Berhasil menghapus {grades_count} nilai dan {reports_count} laporan untuk tahun {year}."
        except Exception as e:
            db.session.rollback()
            raise e
