from flask import Flask, render_template, request, session, jsonify, redirect, url_for
import sqlite3
import hashlib
import json
from datetime import datetime, date
import secrets
import os

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# ============================================
# DATABASE FUNCTIONS
# ============================================

def get_db():
    conn = sqlite3.connect('school.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute("DROP TABLE IF EXISTS messages")
    cursor.execute("DROP TABLE IF EXISTS contacts")
    cursor.execute("DROP TABLE IF EXISTS attendance")
    cursor.execute("DROP TABLE IF EXISTS assignments")
    cursor.execute("DROP TABLE IF EXISTS results")
    cursor.execute("DROP TABLE IF EXISTS news")
    cursor.execute("DROP TABLE IF EXISTS students")
    cursor.execute("DROP TABLE IF EXISTS teachers")
    cursor.execute("DROP TABLE IF EXISTS parents")
    
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'student',
            phone TEXT,
            gender TEXT,
            dob TEXT,
            address TEXT,
            grade TEXT,
            section TEXT,
            student_id TEXT UNIQUE,
            subject TEXT,
            department TEXT,
            child_name TEXT,
            child_grade TEXT,
            child_section TEXT,
            status TEXT DEFAULT 'active',
            profile_picture TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            last_login TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            student_id TEXT UNIQUE,
            grade TEXT,
            section TEXT,
            parent_email TEXT,
            parent_name TEXT,
            parent_phone TEXT,
            enrolled_date TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            subject TEXT,
            department TEXT,
            qualification TEXT,
            experience_years INTEGER DEFAULT 0,
            hire_date TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE parents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            children TEXT DEFAULT '[]',
            occupation TEXT,
            address TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            read INTEGER DEFAULT 0,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            room TEXT,
            FOREIGN KEY (sender_id) REFERENCES users(id),
            FOREIGN KEY (receiver_id) REFERENCES users(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            contact_id INTEGER NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (contact_id) REFERENCES users(id),
            UNIQUE(user_id, contact_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            grade TEXT NOT NULL,
            section TEXT NOT NULL,
            date TEXT NOT NULL,
            status TEXT DEFAULT 'present',
            remark TEXT,
            teacher_id INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES users(id),
            FOREIGN KEY (teacher_id) REFERENCES users(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id INTEGER NOT NULL,
            subject TEXT NOT NULL,
            grade TEXT NOT NULL,
            section TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            due_date TEXT NOT NULL,
            total_marks INTEGER DEFAULT 100,
            status TEXT DEFAULT 'active',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (teacher_id) REFERENCES users(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            subject TEXT NOT NULL,
            exam_type TEXT NOT NULL,
            score REAL NOT NULL,
            grade TEXT NOT NULL,
            teacher_id INTEGER,
            published_at TEXT DEFAULT CURRENT_TIMESTAMP,
            grade_level TEXT,
            section TEXT,
            FOREIGN KEY (student_id) REFERENCES users(id),
            FOREIGN KEY (teacher_id) REFERENCES users(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            content TEXT NOT NULL,
            date TEXT DEFAULT CURRENT_DATE,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (author_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database created successfully!")

def hash_password(password):
    salt = "school_salt_2024"
    return hashlib.sha256((password + salt).encode()).hexdigest()

def create_admin():
    conn = get_db()
    cursor = conn.cursor()
    
    admin = cursor.execute("SELECT * FROM users WHERE role = 'admin'").fetchone()
    if not admin:
        cursor.execute('''
            INSERT INTO users (name, email, username, password_hash, role, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('Admin', 'admin@school.com', 'admin', hash_password('admin123'), 'admin', 'active'))
        conn.commit()
        print("✅ Admin created: admin@school.com / admin123")
    
    conn.close()

# Initialize database
if not os.path.exists('school.db'):
    init_db()
    create_admin()
else:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    if not cursor.fetchone():
        init_db()
        create_admin()
    conn.close()

# ============================================
# PAGE ROUTES - ALL PAGES
# ============================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/signup')
def signup_page():
    return render_template('signup.html')

@app.route('/studenthome')
def student_home():
    if 'user_id' not in session:
        return redirect('/login')
    
    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()
    
    user = cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    student = cursor.execute("SELECT * FROM students WHERE user_id = ?", (user_id,)).fetchone()
    results_count = cursor.execute("SELECT COUNT(*) FROM results WHERE student_id = ?", (user_id,)).fetchone()[0]
    attendance_count = cursor.execute("SELECT COUNT(*) FROM attendance WHERE student_id = ?", (user_id,)).fetchone()[0]
    unread_count = cursor.execute("SELECT COUNT(*) FROM messages WHERE receiver_id = ? AND read = 0", (user_id,)).fetchone()[0]
    
    conn.close()
    return render_template('studenthome.html', user=user, student=student, results_count=results_count, attendance_count=attendance_count, unread_count=unread_count)

@app.route('/teacherhome')
def teacher_home():
    if 'user_id' not in session:
        return redirect('/login')
    
    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()
    
    user = cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    teacher = cursor.execute("SELECT * FROM teachers WHERE user_id = ?", (user_id,)).fetchone()
    students_count = cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'student'").fetchone()[0]
    assignments_count = cursor.execute("SELECT COUNT(*) FROM assignments WHERE teacher_id = ?", (user_id,)).fetchone()[0]
    results_count = cursor.execute("SELECT COUNT(*) FROM results WHERE teacher_id = ?", (user_id,)).fetchone()[0]
    unread_count = cursor.execute("SELECT COUNT(*) FROM messages WHERE receiver_id = ? AND read = 0", (user_id,)).fetchone()[0]
    
    conn.close()
    return render_template('teacherhome.html', user=user, teacher=teacher, students_count=students_count, assignments_count=assignments_count, results_count=results_count, unread_count=unread_count)

@app.route('/parenthome')
def parent_home():
    if 'user_id' not in session:
        return redirect('/login')
    
    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()
    
    user = cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    parent = cursor.execute("SELECT * FROM parents WHERE user_id = ?", (user_id,)).fetchone()
    unread_count = cursor.execute("SELECT COUNT(*) FROM messages WHERE receiver_id = ? AND read = 0", (user_id,)).fetchone()[0]
    
    conn.close()
    return render_template('parenthome.html', user=user, parent=parent, unread_count=unread_count)

@app.route('/adminhome')
def admin_home():
    if 'user_id' not in session:
        return redirect('/login')
    
    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()
    
    user = cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    students_count = cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'student'").fetchone()[0]
    teachers_count = cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'teacher'").fetchone()[0]
    parents_count = cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'parent'").fetchone()[0]
    admins_count = cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'").fetchone()[0]
    assignments_count = cursor.execute("SELECT COUNT(*) FROM assignments").fetchone()[0]
    results_count = cursor.execute("SELECT COUNT(*) FROM results").fetchone()[0]
    unread_count = cursor.execute("SELECT COUNT(*) FROM messages WHERE receiver_id = ? AND read = 0", (user_id,)).fetchone()[0]
    
    conn.close()
    return render_template('adminhome.html', user=user, students_count=students_count, teachers_count=teachers_count, parents_count=parents_count, admins_count=admins_count, assignments_count=assignments_count, results_count=results_count, unread_count=unread_count)

# Other pages
@app.route('/admin-report')
def admin_report():
    return render_template('admin-report.html')

@app.route('/about')
def about():
    return render_template('about us.html')

@app.route('/attendance')
def attendance():
    return render_template('attendance.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

@app.route('/liberary')
def liberary():
    return render_template('liberary.html')

@app.route('/library')
def library():
    return render_template('liberary.html')

@app.route('/manage-parents')
def manage_parents():
    return render_template('manage-parents.html')

@app.route('/manage-students')
def manage_students():
    return render_template('manage-students.html')

@app.route('/manage-teachers')
def manage_teachers():
    return render_template('manage-teachers.html')

@app.route('/messages')
def messages():
    return render_template('messages.html')

@app.route('/post-assignment')
def post_assignment():
    return render_template('post-assignment.html')

@app.route('/post-attendance')
def post_attendance():
    return render_template('post-attendance.html')

@app.route('/post-news')
def post_news():
    return render_template('post-news.html')

@app.route('/post-result')
def post_result():
    return render_template('post-result.html')

@app.route('/results')
def results():
    return render_template('results.html')

@app.route('/students')
def students():
    return render_template('students.html.html')

@app.route('/news')
def news():
    return render_template('news.html')

@app.route('/teachers')
def teachers():
    return render_template('teachers.html')

@app.route('/assignment')
def assignment():
    return render_template('assignment.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# ============================================
# API ROUTES - AUTHENTICATION
# ============================================

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')
    
    conn = get_db()
    cursor = conn.cursor()
    user = cursor.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if hash_password(password) != user['password_hash']:
        return jsonify({'error': 'Invalid password'}), 401
    
    if user['role'] != role:
        return jsonify({'error': f'Invalid role. You are registered as {user["role"]}'}), 403
    
    if user['status'] != 'active':
        return jsonify({'error': 'Account is inactive'}), 403
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET last_login = ? WHERE id = ?", 
                   (datetime.now().isoformat(), user['id']))
    conn.commit()
    conn.close()
    
    session['user_id'] = user['id']
    session['user_role'] = user['role']
    session['user_name'] = user['name']
    session['user_email'] = user['email']
    
    return jsonify({
        'success': True,
        'user': dict(user),
        'redirect': f'/{user["role"]}home'
    }), 200

@app.route('/api/auth/signup', methods=['POST'])
def api_signup():
    data = request.get_json()
    conn = get_db()
    cursor = conn.cursor()
    
    existing = cursor.execute("SELECT * FROM users WHERE email = ?", (data.get('email'),)).fetchone()
    if existing:
        conn.close()
        return jsonify({'error': 'Email already registered'}), 400
    
    if data.get('username'):
        existing = cursor.execute("SELECT * FROM users WHERE username = ?", (data.get('username'),)).fetchone()
        if existing:
            conn.close()
            return jsonify({'error': 'Username already taken'}), 400
    
    cursor.execute('''
        INSERT INTO users (name, email, username, password_hash, role, phone, gender, address, grade, section, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('name'),
        data.get('email'),
        data.get('username'),
        hash_password(data.get('password')),
        data.get('role', 'student'),
        data.get('phone', ''),
        data.get('gender', ''),
        data.get('address', ''),
        data.get('grade', ''),
        data.get('section', ''),
        'active'
    ))
    user_id = cursor.lastrowid
    
    role = data.get('role', 'student')
    if role == 'student':
        student_id = f"DM-{datetime.now().year}-{str(user_id).zfill(4)}"
        cursor.execute('''
            INSERT INTO students (user_id, student_id, grade, section)
            VALUES (?, ?, ?, ?)
        ''', (user_id, student_id, data.get('grade', 'Grade 10'), data.get('section', 'A')))
    elif role == 'teacher':
        cursor.execute('''
            INSERT INTO teachers (user_id, subject, department)
            VALUES (?, ?, ?)
        ''', (user_id, data.get('subject', 'Mathematics'), data.get('department', 'Science')))
    elif role == 'parent':
        cursor.execute('''
            INSERT INTO parents (user_id, children, address)
            VALUES (?, ?, ?)
        ''', (user_id, '[]', data.get('address', '')))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Account created successfully'}), 201

@app.route('/api/auth/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'success': True}), 200

@app.route('/api/auth/current-user', methods=['GET'])
def api_current_user():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    conn = get_db()
    cursor = conn.cursor()
    user = cursor.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    conn.close()
    
    if not user:
        session.clear()
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({'user': dict(user)}), 200

# ============================================
# API ROUTES - USERS
# ============================================

@app.route('/api/users', methods=['GET'])
def api_get_users():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    role = request.args.get('role')
    search = request.args.get('search', '')
    
    conn = get_db()
    cursor = conn.cursor()
    
    query = "SELECT * FROM users"
    params = []
    conditions = []
    
    if role:
        conditions.append("role = ?")
        params.append(role)
    
    if search:
        conditions.append("(name LIKE ? OR email LIKE ? OR grade LIKE ? OR student_id LIKE ?)")
        params.extend([f'%{search}%', f'%{search}%', f'%{search}%', f'%{search}%'])
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    users = cursor.execute(query, params).fetchall()
    conn.close()
    return jsonify({'users': [dict(u) for u in users]}), 200

@app.route('/api/users/<int:user_id>', methods=['GET'])
def api_get_user(user_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    conn = get_db()
    cursor = conn.cursor()
    user = cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({'user': dict(user)}), 200

@app.route('/api/users', methods=['POST'])
def api_create_user():
    if 'user_id' not in session or session.get('user_role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    conn = get_db()
    cursor = conn.cursor()
    
    existing = cursor.execute("SELECT * FROM users WHERE email = ?", (data.get('email'),)).fetchone()
    if existing:
        conn.close()
        return jsonify({'error': 'Email already exists'}), 400
    
    cursor.execute('''
        INSERT INTO users (name, email, password_hash, role, phone, grade, section, student_id, subject, department, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('name'),
        data.get('email'),
        hash_password(data.get('password', 'password123')),
        data.get('role', 'student'),
        data.get('phone', ''),
        data.get('grade', ''),
        data.get('section', ''),
        data.get('student_id', ''),
        data.get('subject', ''),
        data.get('department', ''),
        'active'
    ))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'User created'}), 201

@app.route('/api/users/<int:user_id>', methods=['PUT'])
def api_update_user(user_id):
    if 'user_id' not in session or session.get('user_role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE users 
        SET name = ?, email = ?, phone = ?, grade = ?, section = ?, student_id = ?, 
            subject = ?, department = ?, status = ?
        WHERE id = ?
    ''', (
        data.get('name'),
        data.get('email'),
        data.get('phone', ''),
        data.get('grade', ''),
        data.get('section', ''),
        data.get('student_id', ''),
        data.get('subject', ''),
        data.get('department', ''),
        data.get('status', 'active'),
        user_id
    ))
    conn.commit()
    conn.close()
    return jsonify({'success': True}), 200

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def api_delete_user(user_id):
    if 'user_id' not in session or session.get('user_role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True}), 200

# ============================================
# API ROUTES - MESSAGES
# ============================================

@app.route('/api/messages', methods=['GET'])
def api_get_messages():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    user_id = session['user_id']
    contact_id = request.args.get('contact_id')
    conn = get_db()
    cursor = conn.cursor()
    
    if contact_id:
        messages = cursor.execute('''
            SELECT m.*, u.name as sender_name, u2.name as receiver_name 
            FROM messages m
            JOIN users u ON m.sender_id = u.id
            JOIN users u2 ON m.receiver_id = u2.id
            WHERE (m.sender_id = ? AND m.receiver_id = ?) OR (m.sender_id = ? AND m.receiver_id = ?)
            ORDER BY m.timestamp ASC
        ''', (user_id, contact_id, contact_id, user_id)).fetchall()
        
        cursor.execute('''
            UPDATE messages SET read = 1 
            WHERE receiver_id = ? AND sender_id = ?
        ''', (user_id, contact_id))
        conn.commit()
        conn.close()
        
        return jsonify({'messages': [dict(m) for m in messages]}), 200
    
    contacts = cursor.execute('''
        SELECT DISTINCT u.* FROM users u
        WHERE u.id IN (
            SELECT sender_id FROM messages WHERE receiver_id = ?
            UNION
            SELECT receiver_id FROM messages WHERE sender_id = ?
        ) AND u.id != ?
    ''', (user_id, user_id, user_id)).fetchall()
    
    result = []
    for contact in contacts:
        latest = cursor.execute('''
            SELECT * FROM messages 
            WHERE (sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?)
            ORDER BY timestamp DESC LIMIT 1
        ''', (user_id, contact['id'], contact['id'], user_id)).fetchone()
        
        unread = cursor.execute('''
            SELECT COUNT(*) FROM messages 
            WHERE receiver_id = ? AND sender_id = ? AND read = 0
        ''', (user_id, contact['id'])).fetchone()[0]
        
        result.append({
            'contact': dict(contact),
            'latest_message': dict(latest) if latest else None,
            'unread_count': unread
        })
    
    conn.close()
    return jsonify({'conversations': result}), 200

@app.route('/api/messages/send', methods=['POST'])
def api_send_message():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    data = request.get_json()
    sender_id = session['user_id']
    receiver_id = data.get('receiver_id')
    text = data.get('text', '').strip()
    
    if not receiver_id or not text:
        return jsonify({'error': 'Receiver and message required'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO messages (sender_id, receiver_id, text, read, timestamp)
        VALUES (?, ?, ?, ?, ?)
    ''', (sender_id, receiver_id, text, 0, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Sent'}), 201

@app.route('/api/messages/unread-count', methods=['GET'])
def api_unread_count():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    conn = get_db()
    cursor = conn.cursor()
    count = cursor.execute(
        "SELECT COUNT(*) FROM messages WHERE receiver_id = ? AND read = 0",
        (session['user_id'],)
    ).fetchone()[0]
    conn.close()
    
    return jsonify({'unread_count': count}), 200

@app.route('/api/messages/mark-read', methods=['POST'])
def api_mark_read():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    data = request.get_json()
    message_id = data.get('message_id')
    conn = get_db()
    cursor = conn.cursor()
    
    if message_id:
        cursor.execute("UPDATE messages SET read = 1 WHERE id = ? AND receiver_id = ?", 
                      (message_id, session['user_id']))
    else:
        cursor.execute("UPDATE messages SET read = 1 WHERE receiver_id = ?", (session['user_id'],))
    
    conn.commit()
    conn.close()
    return jsonify({'success': True}), 200

# ============================================
# API ROUTES - STATS
# ============================================

@app.route('/api/stats', methods=['GET'])
def api_get_stats():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    conn = get_db()
    cursor = conn.cursor()
    
    stats = {
        'students': cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'student'").fetchone()[0],
        'teachers': cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'teacher'").fetchone()[0],
        'parents': cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'parent'").fetchone()[0],
        'admins': cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'").fetchone()[0],
        'messages': cursor.execute("SELECT COUNT(*) FROM messages").fetchone()[0],
        'attendance': cursor.execute("SELECT COUNT(*) FROM attendance").fetchone()[0],
        'assignments': cursor.execute("SELECT COUNT(*) FROM assignments").fetchone()[0],
        'results': cursor.execute("SELECT COUNT(*) FROM results").fetchone()[0],
        'news': cursor.execute("SELECT COUNT(*) FROM news").fetchone()[0],
        'active_users': cursor.execute("SELECT COUNT(*) FROM users WHERE status = 'active'").fetchone()[0]
    }
    
    conn.close()
    return jsonify(stats), 200

# ============================================
# ERROR HANDLING
# ============================================

@app.errorhandler(404)
def not_found(e):
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Page Not Found</title></head>
    <body style="font-family: Arial; max-width: 600px; margin: 50px auto; padding: 20px;">
        <h1 style="color: #DA121A;">Page Not Found</h1>
        <p>The page you are looking for does not exist.</p>
        <p><a href="/" style="color: #047857;">🏠 Go to Homepage</a></p>
        <hr>
        <p><strong>Available Pages:</strong></p>
        <ul>
            <li><a href="/">/</a></li>
            <li><a href="/login">/login</a></li>
            <li><a href="/signup">/signup</a></li>
            <li><a href="/studenthome">/studenthome</a></li>
            <li><a href="/teacherhome">/teacherhome</a></li>
            <li><a href="/parenthome">/parenthome</a></li>
            <li><a href="/adminhome">/adminhome</a></li>
            <li><a href="/messages">/messages</a></li>
            <li><a href="/attendance">/attendance</a></li>
            <li><a href="/results">/results</a></li>
            <li><a href="/gallery">/gallery</a></li>
            <li><a href="/contact">/contact</a></li>
            <li><a href="/about">/about</a></li>
            <li><a href="/liberary">/liberary</a></li>
            <li><a href="/news">/news</a></li>
            <li><a href="/students">/students</a></li>
        </ul>
    </body>
    </html>
    """, 404

# ============================================
# RUN APP
# ============================================

if __name__ == '__main__':
    print("=" * 60)
    print("🏫 Debre Markos Secondary School System")
    print("=" * 60)
    print("📧 Admin Email: admin@school.com")
    print("🔑 Admin Password: admin123")
    print("=" * 60)
    print("🚀 Server running at: http://localhost:5000")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)