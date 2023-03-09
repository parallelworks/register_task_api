"""
Information known:
- Before launching the task: input parameters
- After launching the task: pid, jobid
- When task is completed: runtime
--> Therefore app should be able to call the API when running 

How can we retrieve information about a given task? 
- Need some sort of task name
- Task name needs to be unique

Cant use resource name for training purposes since resource could be edited
- Need to use specific resource properties like instance type
- Could we save resource name and session and use that to retrieve the resource properties?
- Resource properties could be number of CPUs, Mem, instance type, cloud, etc
- We should support an aribitrary number of resource properties like we support an arbitrary number of task inputs
- How about onprem?

If the task inputs are changed we cannot predict the new task

"""

import json

from flask import Flask, render_template

from tasks_bp import tasks_bp, db_tasks, db_tasks_path
from models_bp import models_bp, db_models, db_models_path

TASKS_URL: str = "http://127.0.0.1:5000/tasks"
MODELS_URL: str = "http://127.0.0.1:5000/models"

app = Flask(__name__)
app.register_blueprint(tasks_bp, url_prefix="")
app.register_blueprint(models_bp, url_prefix="")


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = db_tasks_path
db_tasks.init_app(app)

# Configure the second database
app.config['SQLALCHEMY_BINDS'] = {'models': db_models_path}
db_models.init_app(app)

#app.register_blueprint(tasks_bp, url_prefix='/tasks')


@app.route('/')
def index():
    return render_template('index.html')



if __name__ == '__main__':

    with app.app_context():
        db_tasks.create_all()
        db_models.create_all()

    print(app.url_map)
    app.run(debug=True)