# Task Management API

A **RESTful** Flask api for managing tasks with sorting, searching, and filtering capabilities.
First major API app created by author.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt
```

To instantiate the database I found running the following commands in an interactive python shell to be the easiest approach

```python
# Import app and db from app.py
from app import db, app

# Use app context manager to create database
with app.app_context():
    db.create_all()
```
The main **app.py** file has code to start the Flask app API embedded within so it can be ran either way below

```bash
# Using flask command(debug mode OFF by default)
flask run

# Using python command(debug mode ON by default)
python app.py
```

First API Call:
```bash
curl -X GET "http://localhost:5000/api/tasks"
```

## Base URL

http://localhost:5000/api/tasks

## Authentication

No authentication requirements needed. This is just a small practice project.

## Endpoints

### Get All Tasks

> GET /api/tasks

#### Query Parameters

- `search` (string, *optional*): Filter tasks by name containing search term
- `sort` (string, *optional*): Sorts task by field `name`, `due_date`, `priority`, `status`
- `priority` (string, *optional*): Returns tasks with specified priority `Low`, `Medium`, `High`
- `status` (string, *optional*): Returns tasks with specified status `Pending`, `In Progress`, `Completed`
- `due_date` (string, *optional*): Returns tasks with specified due date. Formatted yyyy-mm-dd

#### Example Request

```bash
curl GET "http://localhost:5000/api/tasks?priority=High&sort=due_date"
```

#### Example Response

```json
[
    {
        "due_date": "2025-07-28T00:00:00",
        "id": 2,
        "name": "Complete Flask README.md",
        "priority": "High",
        "status": "In Progress"
    },
    {
        "due_date": "2025-07-30T00:00:00",
        "id": 1,
        "name": "Finish Flask app",
        "priority": "High",
        "status": "In Progress"
    }
]
```

### Create Task

> POST /api/tasks

#### Request Body
```json
{
    "name": "Task name (required)",
    "priority": "Low|Medium|High (optional, defaults to Medium)",
    "status": "Pending|In Progress|Completed (optional, defaults to Pending)",
    "due_date": "YYYY-MM-DD (Optional)"
}
```

#### Example Request
```bash
curl -X POST "http://localhost:5000/api/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Implement testing suite",
    "due_date": "2025-07-29"
  }'
```

#### Example Response
```json
{
    "due_date": "2025-07-29T00:00:00",
    "id": 3,
    "name": "Implement testing suite",
    "priority": "Medium",
    "status": "Pending"
}
```

### Update Task
> PUT /api/tasks/{task_id}

#### Path Parameters
- `{task_id}` (integer, *required*): ID of the task to update

#### Request Body
Same as the request body for POST requests (all fields optional)

#### Example Request
```bash
curl -X PUT "http://localhost:5000/api/tasks/3" \
  -H "Content-Type: application/json" \
  -d '{"status": "In Progress",
       "due_date": "2025-07-31 
    }'
```

#### Example Response
```json
{
    "due_date": "2025-07-31T00:00:00",
    "id": 3,
    "name": "Implement testing suite",
    "priority": "Medium",
    "status": "In Progress"
}
```

### Delete Task
> DELETE /api/task/{task_id}

#### Path Parameters
- {task_id} (integer, *required*): ID of task to be deleted

#### Example Request
```bash
curl -X DELETE "http://localhost:5000/api/tasks/2"
```

#### Example Response
```json
{
    "message": "task successfully deleted"
}
```

### Error Responses

All errors return JSON in the following format:
```json
{
    "details": "additional details (optional)",
    "error": "error description",
    "status": "error status code"
}
```

### Error Response Example
```json
{
    "details": {
        "due_date": [
            "Not a valid datetime."
        ],
        "name": [
            "Shorter than minimum length 2."
        ],
        "status": [
            "Must be one of: Completed, In Progress, Pending."
        ]
    },
    "error": "Invalid data",
    "status": 400
}
```
