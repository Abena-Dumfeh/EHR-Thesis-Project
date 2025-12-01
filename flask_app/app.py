from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

from flask import Flask
from config import Config
from flask_bcrypt import Bcrypt

# Blueprints
from flask_app.patient.routes import patient_bp
from flask_app.doctor.routes import doctor_bp
from flask_app.admin.routes import admin_bp

# Initialize app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize Bcrypt for password hashing
bcrypt = Bcrypt(app)

# Register Blueprints
app.register_blueprint(patient_bp, url_prefix='/patient')
app.register_blueprint(doctor_bp, url_prefix='/doctor')
app.register_blueprint(admin_bp, url_prefix='/admin')

if __name__ == '__main__':
    app.run(debug=True)
