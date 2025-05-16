# 📚 Online Library Management System

This is a web-based Library Management System built with **Flask (Python)**, **HTML/CSS**, **JavaScript**, and **MySQL**. It allows admins and students to manage and interact with a digital library system efficiently.

## 🚀 Features

### 👨‍💼 Admin Panel
- Login/Registration
- Add, Update, Delete Books
- View Registered Students
- Approve/Reject Borrow Requests
- Issue Books
- View and Manage E-Books

### 👨‍🎓 Student Portal
- Login/Registration
- View Available Books
- Borrow Books (with approval system)
- View Borrowed Books
- Read E-Books
- Password Reset with OTP

## 🛠️ Technologies Used
- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python (Flask)
- **Database**: MySQL
- **Tools**: VS Code, XAMPP/WAMP, MySQL Workbench

## 🗂️ Project Structure

Online-Library-management/
│
├── static/ # Static assets (CSS, JS, images)
├── templates/ # HTML templates
├── uploads/ # Folder for E-Books
├── app.py # Main Flask application
├── config.py # Configuration (e.g. DB credentials)
├── requirements.txt # Required Python packages
└── README.md # Project description (this file)


## ⚙️ Setup Instructions

1. **Clone the repository** or extract the ZIP.
2. **Create a virtual environment (optional):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate for Windows

3. Install dependencies:

pip install -r requirements.txt

4.Set up MySQL database:

Import the library.sql file into your MySQL server using phpMyAdmin or MySQL Workbench.

Update your DB credentials in config.py.
5.Run the Flask App:
python app.py
6. Visit in Browser:
http://localhost:5000





🧑‍💻 Author
-------Shaikh Sufinamhek---------