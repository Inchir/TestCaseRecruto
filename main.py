import flask
from flask import render_template
from random import randint

app = flask.Flask(__name__)


@app.route('/generate_code')
def generate_code():
    code = "".join([str(int(randint(0, 9))) for _ in range(4)])
    return render_template('/generate_code.html', code=code)


if __name__ == "__main__":
    app.run("127.0.0.1", 8000, debug=False)
