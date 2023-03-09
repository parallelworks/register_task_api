# May need to delete the database before running
# May need to run before starting the app
export FLASK_APP=application.py
flask db init
flask db migrate
flask db upgrade
