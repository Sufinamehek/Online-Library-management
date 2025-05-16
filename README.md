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



---

### 🔹 Step 2: Upload Your Project to GitHub

#### ✅ Create a GitHub Repository:

1. Go to [GitHub](https://github.com).
2. Login and click the **+** icon > **New repository**.
3. Name it (e.g., `Online-Library-management`) and click **Create repository**.

---

#### ✅ Upload Code via Command Line

1. Open terminal or CMD in your project folder:
```bash
cd path/to/Online-Library-management


🧑‍💻 Author
-------Shaikh Sufinamhek---------