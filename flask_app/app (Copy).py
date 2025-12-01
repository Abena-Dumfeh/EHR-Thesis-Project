from flask import Flask
from config import Config
from flask_bcrypt import Bcrypt

# Import role-specific blueprints
from flask_app.patient.routes import patient_bp
#from flask_app.doctor.upload import doctor_bp
from flask_app.doctor.routes import doctor_bp
from flask_app.admin.routes import admin_bp

app = Flask(__name__)
app.config.from_object(Config)

# Register Blueprints for each user role
app.register_blueprint(patient_bp, url_prefix='/patient')
app.register_blueprint(doctor_bp, url_prefix='/doctor')
app.register_blueprint(admin_bp, url_prefix='/admin')

if __name__ == '__main__':
    app.run(debug=True)
