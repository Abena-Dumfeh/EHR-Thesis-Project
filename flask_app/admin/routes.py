from flask import Blueprint, render_template, request, redirect, url_for, flash
import mysql.connector
from werkzeug.security import generate_password_hash
from flask_bcrypt import Bcrypt

admin_bp = Blueprint('admin_bp', __name__)
bcrypt = Bcrypt()  # Make sure to initialize this in your main app and pass it

# Database connection function (you can customize this)
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='ehruser',
        password='StrongPass2025!',
        database='ehrdb'
    )

@admin_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        contact = request.form['contact']
        password = request.form['password']

        # Hash the password using bcrypt
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Check if email already exists
        cursor.execute("SELECT * FROM admins WHERE email = %s", (email,))
        existing_admin = cursor.fetchone()
        if existing_admin:
            flash('Email is already registered.', 'error')
            cursor.close()
            conn.close()
            return render_template('admin/register.html')

        # Insert new admin
        cursor.execute("""
            INSERT INTO admins (name, email, contact, password_hash)
            VALUES (%s, %s, %s, %s)
        """, (name, email, contact, password_hash))

        conn.commit()
        cursor.close()
        conn.close()

        flash('Registration successful. You can now log in.', 'success')
        return redirect(url_for('admin_bp.login'))

    return render_template('admin/register.html')
