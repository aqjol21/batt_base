from flask import Flask, session
from flask_session.__init__ import Session
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

sess = Session()
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
sess.init_app(app)

# login = LoginManager(app)
# login.login_view = 'login'

bootstrap = Bootstrap(app)
from app import routes, models