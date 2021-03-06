from flask import Flask, g, render_template, flash, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import check_password_hash

import models
import forms

DEBUG = True
PORT = 8000
HOST = '0.0.0.0'

app = Flask(__name__)
app.secret_key = 'let this be the secret key'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(userid):
  try:
    return models.User.get(models.User.id == userid)
  except models.DoesNotExist:
    return None

  
@app.before_request
def before_request():
  """Connect to database before each request"""
  g.db = models.DATABASE
  g.db.connect()
  g.user=current_user

  
@app.after_request
def after_request(response):
  """Disconnect from database after each request"""
  g.db.close
  return response

@app.route('/register', methods=['GET', 'POST'])
def register():
  form = forms.RegisterForm()
  if form.validate_on_submit():
    flash('Registered successfully', 'success')
    models.User.create_user(
      email= form.email.data, 
      password=form.password.data
    )
    return redirect(url_for('index'))
  return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
  form = forms.LoginForm()
  if form.validate_on_submit():
    try:
      user = models.User.get(models.User.email == form.email.data)
      if check_password_hash(user.password, form.password.data):
        login_user(user)
        flash('Logged in successfully', 'success')
        return redirect(url_for('index'))
    except models.DoesNotExist:
      flash("Your email or password don't match", "error")
  else:
    flash("Your email or password doesn't match", "error")
  return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
  logout_user()
  flash('Logged out successfully', 'success')
  return redirect(url_for('index'))

@app.route('/taco', methods=['GET', 'POST'])
@login_required
def taco():
  form = forms.TacoForm()
  if form.validate_on_submit():
    models.Taco.create(user=g.user._get_current_object(),
                       protein=form.protein.data, 
                       shell=form.shell.data, 
                       cheese=form.shell.data, 
                       extras=form.extras.data.strip()
                      )
    flash('Taco has been added', 'success')
    return redirect(url_for('index'))
  return render_template('taco.html', form=form)
  
  
@app.route('/')
def index(): 
  tacos = models.Taco.select().limit(10)
  return render_template('index.html', tacos=tacos)

  
if __name__ == '__main__':
  models.initialize()
  try:
    with models.DATABASE.transaction():
      models.User.create_user(
        email='moyongqaa@gmail.com', 
        password='password'
      )
  except ValueError:
    pass
   
  app.run(debug=DEBUG, host=HOST, port=PORT)