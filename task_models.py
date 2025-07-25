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
    created_on = db.Column(db.DateTime, default=datetime.now())


class TaskSchema(ma.SQLAlchemyAutoSchema):
    name = String(required=True, validate=validate.Length(min=2))
    priority = String(validate=validate.OneOf(['High', 'Medium', 'Low']),
                      load_default='Medium')
    due_date = DateTime(validate=validate.Range(min=datetime.now()))
    status = String(validate=validate.OneOf(['Completed', 'In Progress',
                                            'Pending']), load_default='Pending')

    class Meta:
        model = Task
        # exclude = ['id']
        load_instance = True
        sqla_session = db.session


task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)
