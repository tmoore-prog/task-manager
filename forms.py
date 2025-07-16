from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class TaskForm(FlaskForm):
    task = StringField('New Task', validators=[DataRequired()])
    submit = SubmitField('Add Task')
