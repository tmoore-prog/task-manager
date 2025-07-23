#Task Management API

A **RESTful** Flask api for managing tasks with sorting, searching, and filtering capabilities.
First major API app created by author.

##Quick Start

```bash

# Install dependencies
pip install -r requirements.txt
```

To instantiate the database I found running the following commands in an interactive python shell to be the easiest approach

```python

# Import app and db from app.py
from app import db, app

# Use app context handler to create database
with app.app_context():
    db.create_all()
```
