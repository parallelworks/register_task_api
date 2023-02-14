# Some information is known before launching the task: input parameters
# Other information is known after launching the task: pid, jobid
# --> Therefore app should be able to call the API when running 
# 

# How can we retrieve information about a given task? 
# --> Need some sort of task name
# --> Task name needs to be unique

import json

from flask import Flask, request
from tasks_bp import db_task, tasks_bp


app = Flask(__name__)
app.register_blueprint(tasks_bp, url_prefix="")

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
db_task.init_app(app)

# Configure the second database
#app.config['SQLALCHEMY_BINDS'] = {'data2': 'sqlite:///data_2.db'}
#db2.init_app(app)

#app.register_blueprint(tasks_bp, url_prefix='/tasks')


@app.route('/')
def index():
    return 'Hello'

if __name__ == '__main__':
    print(app.url_map)
    app.run(debug=True)