import pandas as pd
from app.models import Student
from app.core.extensions import db

class ImportService:
    @staticmethod
    def import_students(file_storage):
        """
        Imports students from CSV or Excel file.
        Expected columns: 'nama', 'nis', 'jenis_kelamin' (or 'gender')
        Optional: 'nism', 'status'
        """
        filename = file_storage.filename.lower()
        try:
            if filename.endswith('.csv'):
                df = pd.read_csv(file_storage)
            elif filename.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(file_storage)
            else:
                return False, "Format file tidak didukung. Gunakan CSV atau Excel."
            
            # Normalize headers to lowercase
            df.columns = [c.lower().strip() for c in df.columns]
            
            # Map columns
            # Required: name, nis, gender
            # Mappings allowed:
            # name: 'nama', 'name', 'nama lengkap'
            # nis: 'nis', 'nomor induk'
            # gender: 'l/p', 'gender', 'jenis kelamin', 'jk'
            
            col_map = {}
            for col in df.columns:
                if col in ['nama', 'name', 'nama lengkap']:
                    col_map['name'] = col
                elif col in ['nis', 'nomor induk']:
                    col_map['nis'] = col
                elif col in ['l/p', 'gender', 'jenis kelamin', 'jk']:
                    col_map['gender'] = col
                elif col in ['nism']:
                    col_map['nism'] = col
            
            if 'name' not in col_map or 'nis' not in col_map:
                return False, f"Kolom wajib tidak ditemukan. Pastikan ada kolom 'Nama' dan 'NIS'. Kolom terdeteksi: {list(df.columns)}"
            
            success_count = 0
            errors = []
            
            for index, row in df.iterrows():
                try:
                    nis = str(row[col_map['nis']]).strip()
                    name = str(row[col_map['name']]).strip()
                    
                    if not nis or not name or nis.lower() == 'nan':
                        continue
                        
                    # Check duplicate
                    existing = Student.query.filter_by(nis=nis).first()
                    if existing:
                        errors.append(f"Baris {index+2}: NIS {nis} sudah ada (Dilewati).")
                        continue
                    
                    gender = 'L' # Default
                    if 'gender' in col_map:
                        g_val = str(row[col_map['gender']]).upper().strip()
                        if g_val in ['P', 'PEREMPUAN', 'WANITA']:
                            gender = 'P'
                        elif g_val in ['L', 'LAKI-LAKI', 'PRIA']:
                            gender = 'L'
                    
                    nism = None
                    if 'nism' in col_map:
                        nism = str(row[col_map['nism']]).strip()
                        if nism.lower() == 'nan': nism = None
                        
                    student = Student(
                        name=name,
                        nis=nis,
                        nism=nism,
                        gender=gender,
                        active=True
                    )
                    db.session.add(student)
                    success_count += 1
                    
                except Exception as e:
                    errors.append(f"Baris {index+2}: Error - {str(e)}")
            
            if success_count > 0:
                db.session.commit()
                msg = f"Berhasil mengimpor {success_count} siswa."
                if errors:
                    msg += f" {len(errors)} data dilewati/gagal."
                return True, msg
            else:
                return False, "Tidak ada data yang berhasil diimpor. " + "; ".join(errors[:5])
                
        except Exception as e:
            return False, f"Gagal memproses file: {str(e)}"
