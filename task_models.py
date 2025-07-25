from config import db, ma
from marshmallow.fields import String, Date
from marshmallow import validate
from datetime import datetime


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    priority = db.Column(db.String(20))
    due_on = db.Column(db.Date)
    status = db.Column(db.String(20))
    created_on = db.Column(db.Date, default=datetime.now().date())


class TaskSchema(ma.SQLAlchemyAutoSchema):
    name = String(required=True, validate=validate.Length(min=2, max=50))
    priority = String(validate=validate.OneOf(['High', 'Medium', 'Low']),
                      load_default='Medium')
    due_on = Date(validate=validate.Range(min=datetime.now().date()))
    status = String(validate=validate.OneOf(['Completed', 'In Progress',
                                            'Pending']), load_default='Pending')
    created_on = Date(validate=validate.Equal(datetime.now().date()))

    class Meta:
        model = Task
        # exclude = ['id']
        load_instance = True
        sqla_session = db.session


task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)
