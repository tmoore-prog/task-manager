import time
import uuid
from flask import jsonify, request, abort, g
from config import create_app, db
from task_models import Task, task_schema, tasks_schema
from marshmallow import ValidationError
from datetime import datetime
from sqlalchemy import case
from task_logging import StructuredLogger

api_logger = StructuredLogger(__name__)

app = create_app()


@app.before_request
def before_request():
    g.request_id = str(uuid.uuid4())
    g.start_time = time.time()
    api_logger.info(
        "request started",
        method=request.method,
        path=request.path,
        remote_addr=request.remote_addr,
        user_agent=request.headers.get('User-Agent', ''),
        content_type=request.content_type
    )


@app.after_request
def after_request(response):
    duration = time.time() - g.start_time
    api_logger.info(
        "request_completed",
        method=request.method,
        path=request.path,
        status_code=response.status_code,
        duration_ms=round(duration * 1000, 2),
        response_size=len(response.get_data())
    )
    return response


@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    query = Task.query

    search_term = request.args.get("search")
    if search_term:
        query = query.filter(Task.name.ilike(f'%{search_term}%'))

    priority = request.args.get("priority")
    if priority:
        query = query.filter(Task.priority == priority)

    due_date = request.args.get("due_date")
    if due_date:
        try:
            parsed_date = datetime.strptime(due_date, "%Y-%m-%d").date()

            if hasattr(Task.due_date.type, 'python_type') and \
                    Task.due_date.type.python_type == datetime:
                start_of_day = datetime.combine(parsed_date,
                                                datetime.min.time())
                end_of_day = datetime.combine(parsed_date, datetime.max.time())
                query = query.filter(Task.due_date >= start_of_day,
                                     Task.due_date <= end_of_day)
        except ValueError:
            return jsonify({"error": "invalid date format",
                            "status": 400}), 400

    status = request.args.get("status")
    if status:
        query = query.filter(Task.status == status)

    sort_on = request.args.get("sort")
    if sort_on and not hasattr(Task, sort_on):
        return jsonify({"error": "invalid sort field", "status": 400}), 400
    if sort_on:
        if sort_on == "priority":
            priority_case = case(
                (Task.priority == "Low", 1),
                (Task.priority == "Medium", 2),
                (Task.priority == "High", 3),
                else_=4
            )
            query = query.order_by(priority_case)
        elif sort_on == "status":
            status_case = case(
                (Task.status == "Pending", 1),
                (Task.status == "In Progress", 2),
                (Task.status == "Completed", 3),
                else_=4  # fallback for any unexpected values
            )
            query = query.order_by(status_case)
        else:
            query = query.order_by(getattr(Task, sort_on))

    tasks = query.all()
    if tasks:
        return jsonify(tasks_schema.dump(tasks))
    else:
        abort(404)


@app.route("/api/tasks", methods=["POST"])
def add_task():
    try:
        new_task = task_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"error": "Invalid data", "status": 400,
                        "details": err.messages}), 400
    task = Task.query.filter_by(name=new_task.name).first()
    if task:
        return jsonify({"error": "task already exists", "status": 406}), 406
    db.session.add(new_task)
    db.session.commit()
    return jsonify(task_schema.dump(new_task)), 201


@app.route("/api/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    task = Task.query.get(task_id)
    if task:
        return jsonify(task_schema.dump(task))
    else:
        abort(404)


@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    task_to_update = Task.query.get(task_id)
    if not task_to_update:
        abort(404)
    try:
        task_schema.load(request.get_json(), instance=task_to_update)
    except ValidationError as err:
        return jsonify({"error": "invalid data", "status": 400,
                        "details": err.messages}), 400
    db.session.commit()
    return jsonify(task_schema.dump(task_to_update)), 200


@app.route("/api/tasks/<int:task_id>", methods=['DELETE'])
def delete_task(task_id):
    task_to_delete = Task.query.get(task_id)
    if not task_to_delete:
        abort(404)
    db.session.delete(task_to_delete)
    db.session.commit()
    return jsonify({"message": "task successfully deleted"}), 200


@app.errorhandler(404)
def handle_not_found(e):
    return jsonify({"error": "data not found", "status": 404}), 404


if __name__ == "__main__":
    print("Starting Flask app...")
    app.run(debug=True, host="127.0.0.1", port=5000)
