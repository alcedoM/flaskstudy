from flask import Flask, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

#flask 页面
#上下文处理
@app.context_processor
def inject_user():
    user = User.query.first()
    return dict(user = user)

# 主页面
@app.route('/')
def index():
    movies = Movie.query.all()
    return render_template('index.html', movies=movies)

@app.route('/user/<name>')
def user_page(name):
    return 'User: %s' % name

# 错误页面装饰
@app.errorhandler(404)
def page_not_find(e):
    user = User.query.first()
    return render_template('404.html'), 404

# 数据库主体
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///' + os.path.join(app.root_path, 'data.db')
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    year = db.Column(db.String(4))
    
#数据库更新
import click
@app.cli.command() 
@click.option('--drop', is_flag=True, help='Create after drop.')
def initdb(drop):
    """Initialize the database."""
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')




