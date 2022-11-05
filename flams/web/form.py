from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import SubmitField, IntegerField, SelectMultipleField
from wtforms.validators import (
    NumberRange,
    Optional,
    InputRequired,
)


class InputForm(FlaskForm):
    fasta_file = FileField(
        "Queried sequence",
        validators=[
            FileRequired(),
            FileAllowed([".fa", ".fasta"], "Only fasta files allowed!"),
        ],
    )
    modifications = SelectMultipleField(
        label="Modifications",
        choices=["acetylation"],
        validators=[InputRequired()],
    )
    position = IntegerField(
        "Position of modification",
        validators=[NumberRange(min=1), InputRequired()],
    )
    range = IntegerField("+/- positions", validators=[NumberRange(min=0), Optional()])
    submit = SubmitField("Submit")
