from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from . import auth_bp
from app.models import User

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            flash('Login gagal. Periksa username atau password Anda.')
            return redirect(url_for('auth.login'))
            
        login_user(user, remember=remember)
        # Redirect to next page or dashboard
        next_page = request.args.get('next')
        return redirect(next_page or url_for('dashboard.index'))
        
    return render_template('pages/auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('auth.login'))

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not current_user.check_password(old_password):
            flash('Password lama salah.', 'error')
            return redirect(url_for('auth.change_password'))
            
        if new_password != confirm_password:
            flash('Konfirmasi password baru tidak cocok.', 'error')
            return redirect(url_for('auth.change_password'))
            
        if len(new_password) < 6:
            flash('Password baru minimal 6 karakter.', 'error')
            return redirect(url_for('auth.change_password'))
            
        try:
            current_user.set_password(new_password)
            from app.core.extensions import db
            db.session.commit()
            flash('Password berhasil diubah. Silakan login kembali.', 'success')
            logout_user()
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash(f'Gagal mengubah password: {str(e)}', 'error')
            
    return render_template('pages/auth/change_password.html')
