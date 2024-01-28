from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os



cdir = os.path.abspath(os.path.dirname(__file__))
inst_path = 'instance' #os.path.join(cdir,'assets\\instance')


app = Flask(__name__,static_folder='assets')#,instance_path=inst_path)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(cdir,'appdb.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'ok_boomer'
app.config['WTF_CSRF_ENABLED'] = False
app.config['UPLOAD_FOLDER'] = app.static_folder + '/uploads'  #'assets\\uploads'
app.config['MAX_CONTENT_LENGTH'] = 4 * 1000 * 1000
app.app_context().push()
app.secret_key = 'ParchoonIOApp'


db = SQLAlchemy(app)


import routes#, model

if __name__ == '__main__':
    app.run(
        host = '0.0.0.0',
        debug = True,
        port = 5000,
    )
