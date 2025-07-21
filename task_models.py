from config import db, ma


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    priority = db.Column(db.String(20))
    due_date = db.Column(db.DateTime)
    status = db.Column(db.String(20))


class TaskSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Task
        load_instance = True
        sqla_session = db.session


task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)
