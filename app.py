from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mysqldb import MySQL
from MySQLdb.cursors import DictCursor
from itsdangerous import URLSafeTimedSerializer as Serializer
import base64
import os
import json
from functools import wraps
from datetime import datetime
import MySQLdb
from datetime import date, timedelta
import smtplib
import random
from flask_mail import Mail, Message



# ✅ Flask app config
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'shaikhsufianmehek@gmail.com'     # your Gmail
app.config['MAIL_PASSWORD'] = 'deos cnvt avvz ewqm'        # your App Password, NOT your Gmail password

mail = Mail(app)



# ✅ MySQL config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Mehek'
app.config['MYSQL_DB'] = 'library_db'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

# loan policy constants
LOAN_DAYS    = 14
FINE_PER_DAY = 10



# ✅ Serializer for secure tokens (used in password reset)
s = Serializer(secret_key=app.secret_key)

# ✅ Reusable DB connection
def get_db_connection():
    conn = mysql.connection
    cursor = conn.cursor()
    return conn, cursor




def main():
    if os.path.exists('token.json'):
        print("✅ token.json already exists.")
        return

    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    creds = flow.run_local_server(port=0)

    with open('token.json', 'w') as token:
        token.write(creds.to_json())
    print("✅ token.json created successfully!")



# ✅ Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def login_required_student(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session or session.get('role') != 'student':
            return redirect(url_for('student_login'))
        return f(*args, **kwargs)
    return decorated_function

def login_required_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session or session.get('role') != 'admin':
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session or session.get('role') != 'admin':
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function



# ------------------- Home -------------------
@app.route('/')
def index():
    return render_template('index.html')


# ------------------- Admin Login -------------------
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn, cursor = get_db_connection()
        cursor.execute("SELECT * FROM users WHERE username=%s AND role='admin'", (username,))
        user = cursor.fetchone()
        cursor.close()

        if user and check_password_hash(user['password'], password):
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('admin_portal'))
        else:
            return "Invalid Credentials", 401

    return render_template('admin_login.html')






# ------------------- Student Login -------------------
@app.route("/student_login", methods=["GET", "POST"])
def student_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        conn, cursor = get_db_connection()

        cursor.execute(
            "SELECT * FROM users WHERE username=%s AND password=%s AND role='student'",
            (username, password)
        )
        student = cursor.fetchone()
        cursor.close()
        conn.close()

        if student:
            session.update({
                "username": username,
                "role": "student",
                "student_id": student["id"],
                "user_id": student["id"]
            })
            return redirect(url_for("student_portal"))
        
        flash("Invalid Credentials", "danger")
        
    return render_template("student_login.html")


# ------------------- Admin Portal -------------------
@app.route('/admin_portal', methods=['GET', 'POST'])
@login_required
def admin_portal():
    if session.get('role') != 'admin':
        return redirect(url_for('admin_login'))

    conn, cursor = get_db_connection()  # ✅ FIXED HERE

    cursor.execute("SELECT COUNT(*) AS total_students FROM users WHERE role='student'")
    total_students = cursor.fetchone()['total_students']

    cursor.execute("""
        SELECT u.id, u.username, 
               COUNT(bb.id) AS borrowed_books, 
               COALESCE(u.fine, 0) AS pending_fine 
        FROM users u 
        LEFT JOIN borrowed_books bb ON u.id = bb.student_id 
        WHERE u.role='student' 
        GROUP BY u.id, u.username, u.fine
    """)
    registered_students = cursor.fetchall()

    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()

    cursor.execute("""
        SELECT br.id, u.username AS student_username, b.title AS book_title, br.request_date 
        FROM borrow_requests br 
        JOIN users u ON br.student_id = u.id 
        JOIN books b ON br.book_id = b.id 
        WHERE br.status='pending'
    """)
    book_requests = cursor.fetchall()

    cursor.execute("SELECT id, username, fine FROM users WHERE fine > 0")
    students_with_fines = cursor.fetchall()

    cursor.close()

    return render_template(
        'admin_portal.html',
        total_students=total_students,
        registered_students=registered_students,
        books=books,
        book_requests=book_requests,
        students_with_fines=students_with_fines
    )

    

# ------------------- Student Portal -------------------
def calculate_fine(borrowed_date):
    today = datetime.today().date()
    overdue_days = (today - borrowed_date).days - 7
    return max(overdue_days, 0)
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function  # Corrected

# ------------------ Routes ------------------



@app.route("/student_register", methods=["GET", "POST"])
def student_register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        college_year = request.form["college_year"]
        
        conn, cursor = get_db_connection()
 # No need for cursorclass here if already set in connection
        cursor.execute(
            "INSERT INTO users (username, password, role, college_year) VALUES (%s, %s, 'student', %s)",
            (username, password, college_year)
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("student_login"))
    
    return render_template("student_register.html")



@app.route('/student_portal', methods=['GET', 'POST'])
def student_portal():
    if 'username' not in session or session.get('role') != 'student':
        return redirect(url_for('student_login'))
    conn, cursor = get_db_connection()
    cursor.execute("SELECT id FROM users WHERE username = %s", (session['username'],))
    student = cursor.fetchone()
    student_id = student['id']

    if request.method == 'POST':
        book_id = request.form.get('book_id')
        cursor.execute("SELECT * FROM books WHERE id = %s", (book_id,))
        book = cursor.fetchone()
        if book:
            cursor.execute("INSERT INTO borrowed_books (book_id, student_id, borrowed_date, issue_date) VALUES (%s, %s, %s, %s)",
                           (book_id, student_id, date.today(), date.today()))
            conn.commit()
            flash("Book borrowed successfully!", "success")

    cursor.execute("SELECT * FROM books")
    available_books = cursor.fetchall()
    cursor.execute("SELECT borrowed_books.id AS borrow_id, books.title, books.author, borrowed_books.borrowed_date \
                    FROM borrowed_books JOIN books ON borrowed_books.book_id = books.id \
                    WHERE borrowed_books.student_id = %s AND borrowed_books.return_date IS NULL", (student_id,))
    borrowed_books = cursor.fetchall()
    for book in borrowed_books:
        book['fine'] = calculate_fine(book['borrowed_date'])

    cursor.close()
    return render_template('student_portal.html', books=available_books, borrowed_books=borrowed_books, student_name=session['username'])



@app.route('/pending_borrow_requests')
def pending_borrow_requests():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM borrow_requests WHERE status = 'pending'")
    pending = cursor.fetchall()
    cursor.close()
    return render_template('pending_borrow_requests.html', pending=pending)


from datetime import datetime, timedelta

@app.route('/admin/approve_request', methods=['POST'])
def approve_request():
    request_id = request.form.get('request_id')

    cur = mysql.connection.cursor()

    # Get borrow request details
    cur.execute("SELECT student_id, student_username, book_id, book_title FROM borrow_requests WHERE id = %s", (request_id,))
    request_data = cur.fetchone()

    if request_data:
        student_id, student_username, book_id, book_title = request_data

        issue_date = datetime.now().date()
        due_date = issue_date + timedelta(days=14)  # e.g., due in 2 weeks

        # Insert into issued_books
        cur.execute("""
            INSERT INTO issued_books (student_username, book_title, issue_date, due_date, book_id, student_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (student_username, book_title, issue_date, due_date, book_id, student_id))

        # Optionally delete from borrow_requests
        cur.execute("DELETE FROM borrow_requests WHERE id = %s", (request_id,))
        mysql.connection.commit()
        flash("Book issued successfully!", "success")
    else:
        flash("Request not found.", "error")

    cur.close()
    return redirect(url_for('issued_books'))







@app.route('/admin/reject_request', methods=['POST'])
def reject_request():
    request_id = request.form['request_id']
    
    cur = mysql.connection.cursor()

    try:
        cur.execute("UPDATE borrow_requests SET status = 'rejected' WHERE id = %s", (request_id,))
        mysql.connection.commit()
        flash("Book request rejected!", "warning")
    except Exception as e:
        mysql.connection.rollback()
        flash(f"Error rejecting request: {str(e)}", "danger")
    finally:
        cur.close()

    return redirect(url_for('pending_requests'))
@app.route('/return_book', methods=['POST'])
@login_required_student
def return_book():
    borrow_id = request.form.get('borrow_id')
    
    cur = mysql.connection.cursor()

    # Fetch the issued book by borrow_id
    cur.execute("SELECT * FROM issued_books WHERE id = %s", (borrow_id,))
    issued_book = cur.fetchone()

    if issued_book:
        # Insert into returned_books with only the required columns
        cur.execute("""
            INSERT INTO returned_books (
                student_username, book_title, issue_date, return_date
            )
            VALUES (%s, %s, %s, CURDATE())
        """, (
            issued_book['student_username'],
            issued_book['book_title'],
            issued_book['issue_date']
        ))

        # Delete from issued_books
        cur.execute("DELETE FROM issued_books WHERE id = %s", (borrow_id,))
        mysql.connection.commit()
        flash("Book returned and logged successfully.", "success")
    else:
        flash("Invalid return request.", "danger")

    cur.close()
    return redirect(url_for('your_borrowed_books'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("index"))@app.route('/borrowed_books', methods=['GET', 'POST'])
@app.route('/your_borrowed_books')
@login_required_student
def your_borrowed_books():
    username = session['username']
    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT ib.id, ib.book_id, b.title, b.author, ib.issue_date, ib.due_date
        FROM issued_books ib
        LEFT JOIN books b ON ib.book_id = b.id
        WHERE ib.student_username = %s
    """, (username,))

    data = cur.fetchall()
    cur.close()

    borrowed_books = []
    for row in data:
        borrowed_books.append({
            'borrow_id': row['id'],
            'book_id': row['book_id'] if row['book_id'] else 'N/A',
            'title': row['title'] if row['title'] else 'Unknown Title',
            'author': row['author'] if row['author'] else 'Unknown',
            'borrow_date': row['issue_date'],
            'due_date': row['due_date'],
            'status': 'Not Returned',
            'fine': 0
        })

    return render_template('your_borrowed_books.html', borrowed_books=borrowed_books)



@app.route('/delete_book/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Unauthorized.', 'danger')
        return redirect(url_for('available_books'))

    conn = get_db_connection()
    cursor = conn.cursor(cursorclass=DictCursor)
    cursor.execute("DELETE FROM books WHERE id = %s", (book_id,))
    conn.commit()
    cursor.close()

    flash('Book deleted successfully.', 'success')
    return redirect(url_for('available_books'))

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        pass  # your reset password logic
    return render_template('reset_password.html')

@app.route('/mark_fine_paid/<int:student_id>', methods=['POST'])
@login_required
def mark_fine_paid(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET fine = 0 WHERE id = %s", (student_id,))
    conn.commit()
    cursor.close()
    return redirect(url_for('registered_students'))

@app.route('/students_with_fines')
def students_with_fines():
    if session.get('role') != 'admin':
        return redirect(url_for('admin_portal'))

    conn = get_db_connection()
    cursor = conn.cursor(cursorclass=DictCursor)
    cursor.execute("SELECT id, username, fine FROM users WHERE role = 'student' AND fine > 0")
    students_with_fines = cursor.fetchall()
    cursor.close()
    return render_template('students_with_fines.html', students_with_fines=students_with_fines)

@app.route('/pending_fines')
def pending_fines():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Mehek',
        database='library_db'
    )
    cursor = conn.cursor(cursorclass=DictCursor)
    cursor.execute("SELECT id, username, fine FROM users WHERE fine > 0")
    students_with_fines = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('pending_fines.html', students_with_fines=students_with_fines)

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('index'))  # Use the function name here
    return render_template('admin_index.html')


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']

        cur = mysql.connection.cursor()  # ✅ Use this instead
        cur.execute("INSERT INTO books (title, author) VALUES (%s, %s)", (title, author))
        mysql.connection.commit()
        cur.close()

        flash('Book added successfully!', 'success')  # ✅ show flash message
        return redirect(url_for('add_book'))

    return render_template('add_book.html')



@app.route('/logged_in_students')
def logged_in_students():
    conn, cursor = get_db_connection()

    cursor.execute("SELECT username FROM users WHERE is_logged_in = 1")
    logged_in = cursor.fetchall()
    cursor.close()
    return render_template('logged_in_students.html', logged_in_students=logged_in)

@app.route('/admin/issued_books')
def issued_books():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cur.execute("""
        SELECT 
            ib.id AS id, 
            IFNULL(b.title, ib.book_title) AS title,
            IFNULL(u.username, ib.student_username) AS student,
            ib.issue_date AS issue_date, 
            ib.due_date AS due_date
        FROM issued_books AS ib
        LEFT JOIN books AS b ON ib.book_id = b.id
        LEFT JOIN users AS u ON ib.student_id = u.id
    """)

    rows = cur.fetchall()
    cur.close()

    issued_books_list = []
    for row in rows:
        issued_books_list.append({
            'borrow_id': row['id'],
            'title': row['title'],
            'student': row['student'],
            'borrowed_date': row['issue_date'],
            'return_date': row['due_date'],
        })

    return render_template('issued_books.html', issued_books=issued_books_list)




@app.route('/admin/returned_books')
@login_required_admin
def admin_returned_books():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM returned_books ORDER BY return_date DESC")
    books = cur.fetchall()
    cur.close()
    return render_template('admin_returned_books.html', books=books)





@app.route('/ebooks')
def ebooks():
    ebooks = [
    {"title": "Learn Python", "type": "Programming", "url": "/read/learn_python.pdf"},
    {"title": "Algebra Full Course", "type": "Mathematics", "url": "/read/algebra_full_course.pdf"},
    {"title": "History of the World", "type": "History", "url": "/read/history_of_the_world.pdf"},
]

    return render_template('ebooks.html', ebooks=ebooks)

@app.route('/read/<filename>')
def read_ebook(filename):
    return render_template('read_pdf.html', filename=filename)


@app.route('/registered_students')
@login_required
def registered_students():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Get all students
        cursor.execute("SELECT id, username, fine FROM users WHERE role = 'student'")
        students = cursor.fetchall()

        student_data = []

        for student in students:
            student_id = student['id']
            username = student['username']
            fine = student['fine']

            # Count borrowed books
            cursor.execute("SELECT COUNT(*) AS count FROM borrowed_books WHERE student_id = %s", (student_id,))
            borrowed_books = cursor.fetchone()['count']

            student_data.append({
                'id': student_id,
                'username': username,
                'borrowed_books': borrowed_books,
                'fine': fine
            })

        cursor.close()
        return render_template('registered_students.html', registered_students=student_data)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return "Something went wrong while loading students.", 500




@app.route('/student/available_books')
def student_available_books():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM books WHERE available_copies > 0")
    books = cur.fetchall()
    cur.close()
    return render_template("student_available_books.html", books=books)






   
   
   
@app.route('/available_books')
def available_books():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM books")
    books = cur.fetchall()
    cur.close()
    return render_template('available_books.html', books=books)




@app.route('/student_logout')
def student_logout():
    session.clear()
    return redirect(url_for('student_login'))


def get_all_ebooks():
    conn, cursor = get_db_connection()  # ✅ fix


    cursor.execute("SELECT * FROM ebooks")
    ebooks = cursor.fetchall()

    cursor.close()
    conn.close()
    return ebooks

@app.route('/student_ebooks')
def student_ebooks():
    ebooks = [
        {"title": "Learn Python", "author": "John Doe", "link": "/read/learn_python.pdf"},
        {"title": "Algebra Full Course", "author": "Jane Smith", "link": "/read/algebra_full_course.pdf"},
        {"title": "History of the World", "author": "Tom Brown", "link": "/read/history_of_the_world.pdf"},
    ]
    return render_template('student_ebooks.html', ebooks=ebooks)
@app.route('/student/request_book', methods=['POST'])
def request_book():
    if 'username' not in session or 'student_id' not in session:
        flash('Please login first.', 'error')
        return redirect(url_for('student_login'))

    student_id = session['student_id']
    student_username = session['username']
    book_id = request.form.get('book_id')

    if not book_id:
        flash("Invalid book request.", "error")
        return redirect(url_for('available_books'))

    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Fetch the book title from the books table
        cursor.execute("SELECT title FROM books WHERE id = %s", (book_id,))
        book = cursor.fetchone()

        if not book:
            flash("Book not found.", "error")
            return redirect(url_for('available_books'))

        book_title = book['title']

        # Insert into borrow_requests table
        cursor.execute("""
            INSERT INTO borrow_requests 
                (student_id, student_username, book_id, book_title, status, admin_decision)
            VALUES 
                (%s, %s, %s, %s, %s, %s)
        """, (student_id, student_username, book_id, book_title, 'pending', 'pending'))

        mysql.connection.commit()
        flash('Book request sent successfully!', 'success')

    except Exception as e:
        mysql.connection.rollback()
        flash(f"Error submitting book request: {str(e)}", 'error')

    finally:
        cursor.close()

    return redirect(url_for('student_available_books'))




    @app.route('/borrow', methods=['POST'])
    @login_required
    def borrow_book():
        student_id = session['student_id']
        book_id = request.form['book_id']

        cur = mysql.connection.cursor()

        # Get book title (optional)
        cur.execute("SELECT title FROM books WHERE id = %s", (book_id,))
        book = cur.fetchone()
        book_title = book[0] if book else "Unknown"

        # Insert into borrow_requests table
        cur.execute("""
            INSERT INTO borrow_requests (student_id, student_username, book_id, book_title, status, admin_decision)
            VALUES (%s, %s, %s, %s, 'pending', 'pending')
        """, (student_id, session['username'], book_id, book_title))

        mysql.connection.commit()
        cur.close()
        
        flash("Borrow request submitted successfully!", "success")
        return redirect(url_for('student_dashboard'))




@app.route('/admin_register', methods=['GET', 'POST'])
def admin_register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        conn = mysql.connection  # ✅ yeh galti se tuple mat banao
        cursor = conn.cursor()
        cursor.execute("INSERT INTO admin (name, email, password) VALUES (%s, %s, %s)", (name, email, password))
        conn.commit()
        cursor.close()
        
        return redirect(url_for('admin_login'))
    
    return render_template('admin_register.html')


@app.route('/admin/forgot_password', methods=['GET', 'POST'])
def admin_forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        otp = str(random.randint(100000, 999999))

        msg = Message('Your OTP for Admin Password Reset',
                      sender=app.config['MAIL_USERNAME'],
                      recipients=[email])
        msg.body = f'Your OTP is: {otp}'

        try:
            mail.send(msg)
            session['otp'] = otp  # store OTP for verification
            flash("OTP sent successfully!", "success")
            return render_template('admin_enter_otp.html', email=email)
        except Exception as e:
            print("Error sending email:", e)
            flash("Failed to send email. Check your email and try again.", "danger")

    return render_template('admin_forgot_password.html')



@app.route('/admin/verify_otp', methods=['GET', 'POST'])
def admin_verify_otp():
    if request.method == 'POST':
        otp_entered = request.form['otp']
        if otp_entered == session.get('admin_otp'):
            return redirect(url_for('admin_reset_password'))
        else:
            return "Incorrect OTP. Try again."
    return render_template('admin_verify_otp.html')



@app.route('/admin/reset_password', methods=['GET', 'POST'])
def admin_reset_password():
    if request.method == 'POST':
        new_password = request.form['new_password']
        email = session.get('admin_email')

        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE admin SET password = %s WHERE email = %s", (new_password, email))
        mysql.connection.commit()
        cursor.close()

        session.pop('admin_email', None)
        session.pop('admin_otp', None)

        return "Password reset successful. <a href='/admin_login'>Login</a>"

    return render_template('admin_reset_password.html')



@app.route('/student/forgot_password', methods=['GET', 'POST'])
def student_forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        # Generate OTP
        otp = str(random.randint(100000, 999999))
        session['student_email'] = email
        session['student_otp'] = otp

        msg = Message('Your OTP for Password Reset',
                      sender=app.config['MAIL_USERNAME'],
                      recipients=[email])
        msg.body = f'Your OTP for password reset is {otp}'
        mail.send(msg)

        flash('OTP has been sent to your email.', 'info')
        return redirect(url_for('verify_student_otp'))
    return render_template('student_forgot_password.html')


@app.route('/student/verify_otp', methods=['GET', 'POST'])
def verify_student_otp():
    if request.method == 'POST':
        entered_otp = request.form['otp']
        if entered_otp == session.get('student_otp'):
            return redirect(url_for('reset_student_password'))
        else:
            flash('Invalid OTP', 'danger')
    return render_template('verify_student_otp.html')
@app.route('/student/reset_password', methods=['GET', 'POST'])
def reset_student_password():
    if request.method == 'POST':
        new_password = request.form['new_password']
        email = session.get('student_email')

        # Update password in database
        cur = mysql.connection.cursor()
        cur.execute("UPDATE students SET password = %s WHERE email = %s", (new_password, email))
        mysql.connection.commit()
        cur.close()

        flash('Password reset successfully. Please login.', 'success')
        return redirect(url_for('student_login'))

    return render_template('student_reset_password.html')







# ------------------- Run Flask App -------------------
if __name__ == '__main__':
    app.run(debug=True)

