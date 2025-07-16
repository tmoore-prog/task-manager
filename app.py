from flask import Flask, render_template, url_for
from forms import TaskForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_toughest_key'

tasks = ['Start Flask App', 'Basic Task Route',
         'Add/Delete/Edit Task with Forms', 'Task DB']


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/tasks', methods=['GET', 'POST'])
def task():
    taskform = TaskForm()
    if taskform.validate_on_submit():
        tasks.append(taskform.task.data)
    return render_template('tasks.html', template_tasks=tasks,
                           template_form=taskform)
