# Some information is known before launching the task: input parameters
# Other information is known after launching the task: pid, jobid
# --> Therefore app should be able to call the API when running 
# 

# How can we retrieve information about a given task? 
# --> Need some sort of task name
# --> Task name needs to be unique

import json

from flask import Flask

from tasks_bp import tasks_bp, db_tasks, db_tasks_path
from models_bp import models_bp, db_models, db_models_path

app = Flask(__name__)
app.register_blueprint(tasks_bp, url_prefix="")
app.register_blueprint(models_bp, url_prefix="")


app.config['SQLALCHEMY_DATABASE_URI'] = db_tasks_path
db_tasks.init_app(app)

# Configure the second database
app.config['SQLALCHEMY_BINDS'] = {'models': db_models_path}
db_models.init_app(app)

#app.register_blueprint(tasks_bp, url_prefix='/tasks')


@app.route('/')
def index():
    return 'Hello'

if __name__ == '__main__':
    print(app.url_map)
    app.run(debug=True)