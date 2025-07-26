import pytest
import json
from config import create_app, db
from task_models import task_schema


@pytest.fixture()
def client():
    test_app = create_app(config_type='testing')

    with test_app.test_client() as client:
        with test_app.app_context():
            db.create_all()

            yield client

            db.session.remove()
            db.drop_all()


def test_get_empty_tasks(client):
    response = client.get('/api/tasks')
    assert response.status_code == 404


def test_create_task_success(client):
    data = {
        "name": "Test POST",
        "due_on": "2025-07-29"
        }
    response = client.post('/api/tasks', data=json.dumps(data),
                           content_type='application/json')
    assert response.status_code == 201
    data = response.get_json()
    assert 'id' in data
    assert data['name'] == "Test POST"


def test_get_task_by_id_success(client):
    data = {
        "name": "Example task",
        "due_on": "2025-07-29"
    }
    task = task_schema.load(data)
    db.session.add(task)
    db.session.commit()
    response = client.get('/api/tasks/1')
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == "Example task"
    assert data['id'] == 1


def test_update_task_success(client):
    data = {
        "name": "Example task",
        "due_on": "2025-07-29"
    }
    task = task_schema.load(data)
    db.session.add(task)
    db.session.commit()
    new_data = {
        "name": "Example task",
        "priority": "High"
    }
    response = client.put('/api/tasks/1', data=json.dumps(new_data),
                          content_type='application/json')
    assert response.status_code == 200
    data = response.get_json()
    assert data['priority'] == "High"
    assert data['name'] == "Example task"
    assert data['id'] == 1


def test_task_delete_success(client):
    data = {
        "name": "Example task",
        "due_on": "2025-07-29"
    }
    task = task_schema.load(data)
    db.session.add(task)
    db.session.commit()
    response = client.delete('/api/tasks/1')
    assert response.status_code == 200
    post_delete_response = client.get('/api/tasks/1')
    assert post_delete_response.status_code == 404


def test_create_task_no_name(client):
    data = {
        "priority": "Medium",
        "due_on": "2026-07-10",
        "status": "In Progress"
    }

    response = client.post('/api/tasks', data=json.dumps(data),
                           content_type='application/json')
    assert response.status_code == 400


def test_get_task_by_search(client):
    data = {
        "name": "Find this task with search",
        "priority": "Medium",
        "due_on": "2026-07-10",
        "status": "In Progress"
    }
    task = task_schema.load(data)
    db.session.add(task)
    db.session.commit()
    response = client.get('/api/tasks?search=search',
                          content_type='application/json')
    assert response.status_code == 200


def test_invalid_json(client):
    response = client.post('/api/tasks',
                           data="{'name': 'Bad task json'",
                           content_type='application/json')
    assert response.status_code == 400


def test_invalid_date_format(client):
    data = {
        "name": "Find this task with search",
        "priority": "Medium",
        "due_on": "2026-07-10",
        "status": "In Progress"
    }
    task = task_schema.load(data)
    db.session.add(task)
    db.session.commit()
    response = client.get('/api/tasks?due_on=invalid-date')
    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == "Invalid date format"


def test_invalid_sort_field(client):
    data = {
        "name": "Find this task with search",
        "priority": "Medium",
        "due_on": "2026-07-10",
        "status": "In Progress"
    }
    task = task_schema.load(data)
    db.session.add(task)
    db.session.commit()
    response = client.get('/api/tasks?sort=tasks')
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Invalid sort field"


def test_sorting_by_priority(client):
    data = [{
        "name": "Low priority",
        "priority": "Low",
        "due_on": "2027-10-20"
    }, {
        "name": "High priority",
        "priority": "High",
        "due_on": "2026-10-12"
    }, {
        "name": "Medium priority",
        "priority": "Medium",
        "due_on": "2025-10-19"
    }]
    for datum in data:
        task = task_schema.load(datum)
        db.session.add(task)
        db.session.commit()
    response = client.get('/api/tasks?sort=priority')
    assert response.status_code == 200
    data = response.get_json()
    assert data[0]['priority'] == 'Low'
    assert data[1]['priority'] == 'Medium'
    assert data[2]['priority'] == 'High'


def test_get_task_by_status(client):
    data = [{
        "name": "Low priority",
        "priority": "Low",
        "due_on": "2027-10-20",
        "status": "Pending"
    }, {
        "name": "High priority",
        "priority": "High",
        "due_on": "2026-10-12",
        "status": "In Progress"
    }, {
        "name": "Medium priority",
        "priority": "Medium",
        "due_on": "2025-10-19",
        "status": "Pending"
    }]
    for datum in data:
        task = task_schema.load(datum)
        db.session.add(task)
        db.session.commit()
    response = client.get('/api/tasks?status=Pending')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2


def test_sorting_by_status(client):
    data = [{
        "name": "Low priority",
        "priority": "Low",
        "due_on": "2027-10-20",
        "status": "Completed"
    }, {
        "name": "High priority",
        "priority": "High",
        "due_on": "2026-10-12",
        "status": "In Progress"
    }, {
        "name": "Medium priority",
        "priority": "Medium",
        "due_on": "2025-10-19",
        "status": "Pending"
    }]
    for datum in data:
        task = task_schema.load(datum)
        db.session.add(task)
        db.session.commit()
    response = client.get('/api/tasks?sort=status')
    assert response.status_code == 200
    data = response.get_json()
    assert data[0]['status'] == 'Pending'
    assert data[1]['status'] == 'In Progress'
    assert data[2]['status'] == 'Completed'


def test_update_nonexistent_task(client):
    data = {"priority": "High"}
    response = client.put('/api/tasks/999', data=json.dumps(data),
                          content_type='application/json')
    assert response.status_code == 404
    data = response.get_json()
    assert data['error'] == "Data not found"


def test_create_app_development():
    app = create_app()
    assert app is not None
    assert app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///task.db'


def test_blueprint_registration():
    app = create_app('testing')
    blueprint_names = [bp.name for bp in app.blueprints.values()]
    assert 'api' in blueprint_names
