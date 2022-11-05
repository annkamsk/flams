from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flams.web.process import process_request

from flams.web.form import InputForm


app = Flask(__name__)

# FIXME do not deploy to production before setting proper env vars here!!!
app.config.update(
    DEBUG=True,
    SECRET_KEY="192b9bdd22ab9ed4d12e236c78afcb9a393ec15f71bbf5dc987d54727823bcbf",
)

Bootstrap(app)


@app.route("/", methods=["POST", "GET"])
def index():
    message = ""
    form = InputForm(modifications=["acetylation"])
    if form.validate_on_submit():
        process_request(form)
        message = "Success"
    return render_template("index.html", form=form, message=message, title="Flams")


if __name__ == "__main__":
    app.run(debug=True)
