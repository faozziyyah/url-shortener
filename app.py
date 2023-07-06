from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user 
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from decouple import config
from datetime import datetime
from random import choice
from flask_caching import Cache
import string
import io
import qrcode
from io import BytesIO
from base64 import b64encode

app = Flask(__name__)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)
cache = Cache(app)
app.config.from_object(config("APP_SETTINGS"))

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Flask_Login Stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    urls = db.relationship('ShortUrls', backref='user', lazy='dynamic')
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute!')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

class ShortUrls(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False)
    short_id = db.Column(db.String(20), nullable=False, unique=True)
    created_at = db.Column(db.DateTime(), default=datetime.now(), nullable=False)
    clicks = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    def __repr__(self):
        return '<ShortUrls %r>' % self.original_url

#create form class
class UserForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    password_hash =PasswordField("Password", validators=[DataRequired(), EqualTo('password_hash2', message='Passwords must match')])
    password_hash2 = PasswordField("Confirm Password", validators=[DataRequired()])
    submit = SubmitField("Submit")

# login form
class LoginForm(FlaskForm):
    username = StringField("username", validators=[DataRequired()])
    password = PasswordField("password", validators=[DataRequired()])
    submit = SubmitField("submit")

def generate_short_id(num_of_chars: int):
    """Function to generate short_id of specified number of characters"""
    return ''.join(choice(string.ascii_letters+string.digits) for _ in range(num_of_chars))

def generate_qr_code(url):
    img = qrcode.make(url)
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return img_io

# add user
@app.route('/user/add', methods=['GET', 'POST'])
def register():
    form = UserForm()
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
            user = User(username=form.username.data, email=form.email.data, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        form.username.data = ''
        form.email.data = ''
        form.password_hash.data = ''

        flash("User Added successfully!")
    our_users = User.query.order_by(User.email)
    return render_template("register.html", form=form, our_users=our_users)

#login user
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("Login successful!!")
                return redirect(url_for('index'))
            else:
                flash("Wrong Password, Try Again!")
        else:
            flash("That user does not exist, Try Again!")

    return render_template('login.html', form=form)

# logout 
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You have logged out!")
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
@limiter.limit('10/minutes')
@login_required
def index():
    if request.method == 'POST':
        long_url = request.form.get('long_url')
        short_id = request.form.get('custom_id')

        if short_id and ShortUrls.query.filter_by(short_id=short_id).first() is not None:
            flash('Please enter different custom id!')
            return redirect(url_for('index'))

        if not long_url:
            flash('The URL is required!')
            return redirect(url_for('index'))

        if not short_id:
            short_id = generate_short_id(8)

        new_link = ShortUrls(original_url=long_url, short_id=short_id, created_at=datetime.now(), user_id=current_user.id)
        db.session.add(new_link)
        db.session.commit()
        short_url = request.host_url + short_id

        return render_template('index.html', short_url=short_url)

    return render_template('index.html')

@app.route('/<short_id>')
def redirect_url(short_id):
    link = ShortUrls.query.filter_by(short_id=short_id).first()
    if link:
        link.clicks += 1
        db.session.commit()
        return redirect(link.original_url)
    else:
        flash('Invalid URL')
        return redirect(url_for('index'))

@app.route('/<short_id>/qr_code')
@cache.cached(timeout=30)
@limiter.limit('10/minutes')
def generate_qr_code_url(short_id):
    url = ShortUrls.query.filter_by(short_id=current_user.id).filter_by(short_id=short_id).first()
    #url = ShortUrls.query.filter_by(short_id=short_id).first()
    if url:
        img_io = generate_qr_code(request.host_url + url.short_id)
        return img_io.getvalue(), 200, {'Content-Type': 'image/png'}
    return 'URL not found.'

@app.route('/analytics/<short_id>')
@login_required
def url_analytics(short_id):
    url = ShortUrls.query.filter_by(short_id=short_id).first()
    if url:
        return render_template('analytics.html', url=url)
    return 'URL not found.'

@app.route("/dashboard")
@login_required
def dashboard():
    id = current_user.id
    user = User.query.filter_by(username=User.username).first_or_404()
    user_urls = user.urls.order_by(ShortUrls.created_at.desc())
    host = request.host_url
    return render_template('dashboard.html', user_urls=user_urls, host=host, id=id)

if __name__ == '__main__':
    app.run(debug=True ,port=8080, use_reloader=False)