from application import db_tasks, db_models, app
with app.app_context():
    db_tasks.create_all()
    db_models.create_all()