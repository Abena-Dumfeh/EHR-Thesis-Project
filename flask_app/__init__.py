from flask import Flask
from flask_bcrypt import Bcrypt

# Initialize extensions
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    app.secret_key = 'your_super_secret_key'  # 🔒 Replace with a secure key in production

    # Initialize bcrypt with the app
    bcrypt.init_app(app)

    # Register blueprints
    from flask_app.admin.routes import admin_bp
    from flask_app.patient.routes import patient_bp
    from flask_app.doctor.routes import doctor_bp

    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(patient_bp, url_prefix='/patient')
    app.register_blueprint(doctor_bp, url_prefix='/doctor')

    return app
