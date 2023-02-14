from application import db_task, app
with app.app_context():
    db_task.create_all()