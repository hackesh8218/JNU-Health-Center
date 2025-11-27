from flask import Flask

# for defining the database db in the app.py
from application.database import db #step3


app=None


def create_app():
  app=Flask(__name__)
  
  app.debug=True
  app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///hms.sqlite3" #step3
  db.init_app(app) #step3
  app.app_context().push()
  return app
app=create_app()
app.secret_key = 'any-random-secret-string'

 
from application.controllers import *  # step2

# from application.models import *
if __name__=='__main__':
  #creating a unique admin details once then after i just commneted out 
  # db.create_all()
  # user1=User(name="admin" , email="admin8218@gmail.com",password="admin@8218", role="admin")
  # db.session.add(user1)
  # db.session.commit()


  app.run()
