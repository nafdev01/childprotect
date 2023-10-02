#gui.py
from flaskwebgui import FlaskUI
from django_project.wsgi import application as app

if __name__ == "__main__":
    FlaskUI(app=app, server="django").run()

