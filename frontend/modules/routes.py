# Imports
import requests
from flask import (
    request,
    redirect,
    url_for,
    render_template,
    flash,
    current_app,
    session
)
from .forms import (
    LoginForm,
    RegisterForm
)
from .api import *
from .helper_func import auth_header



# Function Definition
def required_login(func):

    def decorated(*args,**kwargs):
        headers = {
            "User-Agent":request.headers.get('User-Agent'),
            "Authorization":auth_header(current_app.config.get('API_KEY'))
        }
        response = requests.get(api_validatetoken,
                                headers=headers,
                                cookies={'token':session.get('token')}
                                )
        r_content = response.json()

        if r_content['is_token_valid'] == True:
            print('token is valid')
            return func(*args,**kwargs)
        else:
            print('token is invalid')
            return redirect(url_for('login'))

    return decorated



# Routing
def login():
    login_form = LoginForm()
    if request.method == 'POST' and login_form.validate():
        username = login_form.username.data
        password = login_form.password.data

        # Check passwordhash
        headers = {
            "User-Agent":request.headers.get('User-Agent'),
            "Authorization":auth_header(current_app.config['API_KEY'])
        }
        payload = {
            "username":str(username),
            "password": str(password)
        }
        response = requests.post(api_checkpassword,
                                 headers=headers,
                                 json=payload)
        r_content = response.json()

        # Correct username and password
        if response.status_code == 200:
            session['token'] = r_content['token']
            return redirect(url_for('home'))
        
        # 601 = Wrong username or password
        elif response.status_code == 601:
            flash(r_content['message'],'error')
            return redirect(url_for('login'))
    
    return render_template(
        'login.html',
        form=login_form,
        register_url=url_for('register'))

def register():
    register_form = RegisterForm()

    if request.method == 'POST' and register_form.validate():
        username = register_form.username.data
        email = register_form.email.data
        password = register_form.password.data

        # Create user
        headers = {
            "User-Agent":request.headers.get('User-Agent'),
            "Authorization":auth_header(current_app.config['API_KEY'])
        }
        payload = {
            "username":str(username),
            "email":str(email),
            "password": str(password)
        }
        response = requests.post(api_registeruser,
                                 headers=headers,
                                 json=payload)
        r_content = response.json()

        # Successful registration
        if response.status_code == 201:
            flash(r_content['message'],'message')
            return redirect(url_for('login'))
        
        # 602 = Invalid username or email
        elif response.status_code == 602:
            flash(r_content['message'],'error')
            return redirect(url_for('register'))
    
    return render_template(
        'register.html',
        form=register_form,
        login_url=url_for('login'))

@required_login
def home():
    return '<h1>Home Page</h1>'