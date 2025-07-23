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
        "due_date": "2025-07-29"
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
        "due_date": "2025-07-29"
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
        "due_date": "2025-07-29"
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
        "due_date": "2025-07-29"
    }
    task = task_schema.load(data)
    db.session.add(task)
    db.session.commit()
    response = client.delete('/api/tasks/1')
    assert response.status_code == 200
    post_delete_response = client.get('/api/tasks/1')
    assert post_delete_response.status_code == 404
