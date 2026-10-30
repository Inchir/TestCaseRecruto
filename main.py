import flask
from flask import render_template, redirect, session
from flask_login import LoginManager, login_user, login_required

from models import create_session, global_init
from forms import RegisterForm, LoginForm
from models import User

from random import randint

from dotenv import load_dotenv
import os

load_dotenv()

app = flask.Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'sign_in'


@login_manager.user_loader
def load_user(user_id):
    with create_session() as db_sess:
        return db_sess.get(User, user_id)


@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    # session.clear()
    form = RegisterForm()

    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('sign_up.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        with create_session() as db_sess:

            if db_sess.query(User).filter(User.name == form.name.data).first():
                return render_template('sign_up.html', title='Регистрация',
                                       form=form,
                                       message="Такой пользователь уже есть")
            user = User(
                name=form.name.data
            )
            user.set_password(form.password.data)
            db_sess.add(user)
            db_sess.commit()
            return redirect('/sign_in')
    return render_template('sign_up.html', title='Регистрация', form=form)


@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    # session.clear()
    form = LoginForm()

    if form.validate_on_submit():
        with create_session() as db_sess:
            user = db_sess.query(User).filter(User.name == form.name.data).first()
            if user and user.check_password(form.password.data):
                login_user(user)
                session["visit_count"] = 0
                return redirect("/generate_code_with_login")
            return render_template('sign_in.html',
                                   message="Неправильный логин или пароль",
                                   form=form)
    return render_template('sign_in.html', title='Вход', form=form)


@app.route('/')
def main():
    return render_template('base.html')


@app.route('/generate_code')
def generate_code():
    code = "".join([str(randint(0, 9)) for _ in range(4)])
    return render_template('generate_code.html', code=code)


@app.route("/generate_code_with_login")
@login_required
def generate_code_with_login():
    visit_count = session.get("visit_count", 0)
    # print(visit_count, session.get("visit_count", 0))
    if visit_count > 0:
        session.clear()
        return redirect("/sign_in")
    session["visit_count"] = visit_count + 1

    code = "".join([str(randint(0, 9)) for _ in range(4)])
    return render_template('generate_code_with_login.html', code=code)


base_dir = os.path.dirname(os.path.abspath(__file__))
db_dir = os.path.join(base_dir, "db")
os.makedirs(db_dir, exist_ok=True)

global_init(os.path.join(db_dir, "users.db"))

if __name__ == "__main__":
    app.run("127.0.0.1", 8000, debug=False)
