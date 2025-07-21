from flask import jsonify, request, abort
from config import create_app, db
from task_models import Task, task_schema, tasks_schema
from marshmallow import ValidationError

app = create_app()


@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    tasks = Task.query.all()
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
