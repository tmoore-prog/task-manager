import time
import uuid
from flask import jsonify, request, g, Blueprint
from config import db
from task_models import Task, task_schema, tasks_schema
from marshmallow import ValidationError
from datetime import datetime
from sqlalchemy import case, select
from task_logging import StructuredLogger
from functools import wraps
from sqlalchemy.exc import SQLAlchemyError


api_logger = StructuredLogger(__name__)
api_bp = Blueprint('api', __name__)


def log_api_action(action_name):
    # Decorator to log each api action
    def decorator(f):
        @wraps(f)
        def decorated_func(*args, **kwargs):
            api_logger.info(f"{action_name}_started",
                            endpoint=request.endpoint,
                            args=str(args),
                            kwargs=str(kwargs))

            try:
                result = f(*args, **kwargs)

                if isinstance(result, tuple) and len(result) == 2:
                    response, status_code = result
                    if status_code >= 400:  # HTTP error status
                        api_logger.info(f"{action_name}_failed",
                                        endpoint=request.endpoint,
                                        status_code=status_code)
                    else:
                        api_logger.info(f"{action_name}_completed",
                                        endpoint=request.endpoint,
                                        success=True)
                else:
                    api_logger.info(f"{action_name}_completed",
                                    endpoint=request.endpoint,
                                    success=True)

                return result

            except Exception as e:
                api_logger.error(f"{action_name}_failed",
                                 endpoint=request.endpoint,
                                 error_type=type(e).__name__,
                                 error_message=str(e),
                                 success=False)
                raise

        return decorated_func
    return decorator


@api_bp.before_request
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


@api_bp.after_request
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


@api_bp.route("/api/tasks", methods=["GET"])
@log_api_action("get_tasks")
def get_tasks():
    query = select(Task)

    search_term = request.args.get("search")
    if search_term:
        query = query.where(Task.name.ilike(f'%{search_term}%'))

    priority = request.args.get("priority")
    if priority:
        query = query.where(Task.priority == priority)

    due_date = request.args.get("due_date")
    if due_date:
        try:
            parsed_date = datetime.strptime(due_date, "%Y-%m-%d").date()
            query = query.where(Task.due_date == parsed_date)
        except ValueError as err:
            api_logger.error("invalid_date_entered",
                             reason=str(err))
            return jsonify({"error": "Invalid date format",
                            "details": str(err),
                            "status": 400}), 400

    status = request.args.get("status")
    if status:
        query = query.where(Task.status == status)

    sort_on = request.args.get("sort")
    if sort_on and not hasattr(Task, sort_on):
        api_logger.error("invalid_sort_field",
                         details="sort field needs to be in "
                         "['name', 'due_date', 'priority', 'status', 'id']")
        return jsonify({"error": "Invalid sort field", "status": 400}), 400
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

    result = db.session.execute(query)
    tasks = result.scalars().all()

    if tasks:
        return jsonify(tasks_schema.dump(tasks))
    else:
        api_logger.error("task_not_found",)
        return jsonify({"error": "data not found", "status": 404}), 404


@api_bp.route("/api/tasks", methods=["POST"])
@log_api_action("create_task")
def add_task():
    try:
        new_task = task_schema.load(request.get_json())
    except ValidationError as err:
        api_logger.error("task_validation_failed",
                         reason=err.messages)
        return jsonify({"error": "Invalid data",
                        "details": err.messages,
                        "status": 400}), 400

    task = db.session.execute(select(Task).where(Task.name ==
                                                 new_task.name)).scalar()
    if task:
        api_logger.error("task_creation_failed",
                         reason="task already exists")
        return jsonify({"error": "Task already exists", "status": 406}), 406

    try:
        db.session.add(new_task)
        db.session.commit()
        return jsonify(task_schema.dump(new_task)), 201
    except SQLAlchemyError as err:
        db.session.rollback()
        api_logger.error("database_error", error=str(err))
        return jsonify({"error": "Database error", "status": 500}), 500


@api_bp.route("/api/tasks/<int:task_id>", methods=["GET"])
@log_api_action("get_task_by_id")
def get_task(task_id):
    task = db.session.get(Task, task_id)
    if task:
        return jsonify(task_schema.dump(task))
    else:
        api_logger.error("task_not_found",)
        return jsonify({"error": "data not found", "status": 404}), 404


@api_bp.route("/api/tasks/<int:task_id>", methods=["PUT"])
@log_api_action("update_task")
def update_task(task_id):
    task_to_update = db.session.get(Task, task_id)
    if not task_to_update:
        api_logger.error("task_not_found",)
        return jsonify({"error": "Data not found", "status": 404}), 404
    try:
        task_schema.load(request.get_json(), instance=task_to_update)
        db.session.commit()
        return jsonify(task_schema.dump(task_to_update)), 200

    except ValidationError as err:
        api_logger.error(
            "task_validation_failed",
            reason=err.messages
        )
        return jsonify({"error": "invalid data", "status": 400,
                        "details": err.messages}), 400

    except SQLAlchemyError as err:
        db.session.rollback()
        api_logger.error("database_error", error=str(err))
        return jsonify({"error": "Database error", "status": 500}), 500


@api_bp.route("/api/tasks/<int:task_id>", methods=['DELETE'])
@log_api_action("delete_task")
def delete_task(task_id):
    task_to_delete = db.session.get(Task, task_id)
    if not task_to_delete:
        api_logger.error("task_not_found",)
        return jsonify({"error": "data not found", "status": 404}), 404

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return jsonify({"message": "task successfully deleted"}), 200

    except SQLAlchemyError as err:
        db.session.rollback()
        api_logger.error("database_error", error=str(err))
        return jsonify({"error": "Database error", "status": 500}), 500
