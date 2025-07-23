import pytest
import json
from config import create_app, db
from task_models import Task



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

