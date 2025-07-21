from config import db, ma
from marshmallow.fields import String, DateTime
from marshmallow import validate
from datetime import datetime


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    priority = db.Column(db.String(20))
    due_date = db.Column(db.DateTime)
    status = db.Column(db.String(20))


class TaskSchema(ma.SQLAlchemyAutoSchema):
    name = String(required=True, validate=validate.Length(min=2))
    priority = String(validate=validate.OneOf(['High', 'Medium', 'Low']))
    due_date = DateTime(validate=validate.Range(min=datetime.now()))
    status = String(validate=validate.OneOf(['Done', 'In Progress',
                                            'Planned']))

    class Meta:
        model = Task
        # exclude = ['id']
        load_instance = True
        sqla_session = db.session


task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)
