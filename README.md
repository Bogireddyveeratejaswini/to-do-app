# 📝 To-Do List Application

A simple, user-friendly, and responsive To-Do List web application designed to help users organize daily activities, manage tasks, set priorities, and track their productivity.

🌐 **Live Demo:** [https://to-do-app-347c.onrender.com](https://to-do-app-347c.onrender.com)

📂 **GitHub Repository:** [To-Do App](https://github.com/Bogireddyveeratejaswini/to-do-app)

---

## ✨ Features

- **User Authentication:** Register and log in securely using email and password.
- **Add Tasks:** Create tasks with titles, categories, priorities, and due dates.
- **Edit Tasks:** Update existing task information whenever needed.
- **Delete Tasks:** Remove tasks that are no longer required.
- **Task Completion:** Mark tasks as completed or pending.
- **Priority Management:** Organize tasks into High, Medium, and Low priorities.
- **Task Categories:** Categorize tasks into Work, Study, Personal, Shopping, and Other.
- **Search Tasks:** Quickly find tasks using their titles.
- **Filter Tasks:** Filter tasks based on completion status and category.
- **Sort Tasks:** Organize tasks by newest, oldest, priority, or due date.
- **Progress Tracking:** View total, completed, and pending task counts.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Flask | Web application framework |
| SQLite | Database management |
| HTML5 | Web page structure |
| CSS3 | Styling and responsive design |
| Jinja2 | Dynamic HTML templates |
| Gunicorn | Production WSGI server |
| Render | Application deployment |
| Git & GitHub | Version control and source code hosting |

## 📁 Project Structure

```text
to-do-app/
│
├── app.py                 # Flask application
├── database.db           # SQLite database
├── requirements.txt      # Python dependencies
│
├── static/
│   └── style.css         # Application styling
│
├── templates/
│   ├── index.html        # Main task dashboard
│   ├── login.html        # User login page
│   └── register.html     # User registration page
│
└── README.md             # Project documentation
```

## ⚙️ Installation and Setup

Follow these steps to run the project on your local computer.

### 1. Clone the repository

```bash
git clone https://github.com/Bogireddyveeratejaswini/to-do-app.git
```

### 2. Navigate to the project directory

```bash
cd to-do-app
```

### 3. Create a virtual environment (recommended)

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the application

```bash
python app.py
```

### 6. Open the application

Visit the following URL in your browser:

```text
http://127.0.0.1:5000
```

Register an account and start managing your tasks!

## 🚀 Deployment

This application is deployed using **Render**.

- Hosting Platform: Render
- Source Code: GitHub
- Backend: Python Flask
- Production Server: Gunicorn

**Live Application:** [Open To-Do List Application](https://to-do-app-347c.onrender.com)

## 🔐 Security

- Passwords are stored using password hashing.
- Login-protected routes restrict access to task management.
- Each user can manage their own tasks.
- Flask sessions maintain user login information.

For production deployment, configure a strong Flask `SECRET_KEY` using Render environment variables. Persistent database storage should also be configured to protect SQLite data across service restarts and deployments.

## 🎯 Project Objective

The main objective of this project is to develop a practical task management application while learning the fundamentals of Python web development, database integration, user authentication, and cloud deployment.

## 📚 What I Learned

Through this project, I gained practical experience in:

- Developing web applications using Python and Flask.
- Connecting a web application with an SQLite database.
- Implementing user registration and login functionality.
- Performing CRUD (Create, Read, Update, Delete) operations.
- Designing web pages using HTML and CSS.
- Managing project files using Git and GitHub.
- Deploying a Python web application using Render.

## 🔮 Future Enhancements

- Task reminder notifications.
- Password reset functionality.
- Calendar-based task management.
- Dark mode.
- Export tasks to CSV or PDF.
- Improved database hosting for persistent cloud storage.

## 👨‍💻 Author

**Bogireddyveeratejaswini**

- GitHub: [@Bogireddyveeratejaswini](https://github.com/Bogireddyveeratejaswini)

---

⭐ If you find this project useful, consider giving the repository a star!

**Thank you for visiting my project!**
