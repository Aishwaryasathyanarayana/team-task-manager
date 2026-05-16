from flask import Flask, render_template, redirect, request, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User, Project, Task
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def home():
    return redirect("/login")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])
        role = request.form["role"]

        user = User(name=name, email=email, password=password, role=role)
        db.session.add(user)
        db.session.commit()
        flash("Account created successfully")
        return redirect("/login")

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect("/dashboard")

        flash("Invalid credentials")

    return render_template("login.html")


@app.route("/dashboard")
@login_required
def dashboard():
    projects = Project.query.count()
    tasks = Task.query.count()
    completed = Task.query.filter_by(status="Done").count()

    return render_template(
        "dashboard.html",
        projects=projects,
        tasks=tasks,
        completed=completed
    )


@app.route("/projects")
@login_required
def projects():
    all_projects = Project.query.all()
    return render_template("projects.html", projects=all_projects)


@app.route("/create-project", methods=["GET", "POST"])
@login_required
def create_project():
    if request.method == "POST":
        project = Project(
            name=request.form["name"],
            description=request.form["description"],
            deadline=request.form["deadline"],
            created_by=current_user.id
        )
        db.session.add(project)
        db.session.commit()
        return redirect("/projects")

    return render_template("create_project.html")


@app.route("/tasks")
@login_required
def tasks():
    all_tasks = Task.query.all()
    return render_template("tasks.html", tasks=all_tasks)


@app.route("/create-task", methods=["GET", "POST"])
@login_required
def create_task():
    users = User.query.all()
    projects = Project.query.all()

    if request.method == "POST":
        task = Task(
            title=request.form["title"],
            description=request.form["description"],
            due_date=request.form["due_date"],
            assigned_to=request.form["assigned_to"],
            project_id=request.form["project_id"]
        )
        db.session.add(task)
        db.session.commit()
        return redirect("/tasks")

    return render_template(
        "create_task.html",
        users=users,
        projects=projects
    )


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)