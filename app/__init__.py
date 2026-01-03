from flask import Flask, render_template
from config import config
from .core.extensions import init_extensions, db

def create_app(config_name='default'):
    app = Flask(__name__, 
                template_folder='../web/templates',
                static_folder='../web/static')
    
    app.config.from_object(config[config_name])
    
    init_extensions(app)
    register_blueprints(app)
    register_error_handlers(app)
    
    # Auto-Create DB & Admin if not exists (Critical for Vercel/First Run)
    with app.app_context():
        try:
            db.create_all()
            
            # Check and Create Admin User
            from app.models.user import User
            if not User.query.first():
                print("⚠️ No users found. Creating default admin...")
                admin = User(username='admin', email='admin@sekolah.id', role='admin')
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                print("✅ Default admin created: user='admin', pass='admin123'")
        except Exception as e:
            print(f"❌ Database initialization error: {e}")

    # Inject Settings function to all templates
    @app.context_processor
    def inject_settings():
        from app.models.setting import Setting
        def get_setting(key, default=''):
            # Avoid error if db not ready
            try: return Setting.get_value(key, default)
            except: return default
        return dict(get_setting=get_setting)
    
    return app

def register_blueprints(app):
    from app.modules.auth import auth_bp
    from app.modules.dashboard import dashboard_bp
    from app.modules.students import students_bp
    from app.modules.grades import grades_bp
    from app.modules.reports import reports_bp
    from app.modules.settings import settings_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(students_bp, url_prefix='/students')
    app.register_blueprint(grades_bp, url_prefix='/grades')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    app.register_blueprint(settings_bp, url_prefix='/settings')

def register_error_handlers(app):
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('pages/errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('pages/errors/500.html'), 500
