import os
from app import create_app
from app.core.extensions import db
from app.models import User # Import models to ensure they are registered

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User)

if __name__ == '__main__':
    app.run(debug=True, port=5005)
