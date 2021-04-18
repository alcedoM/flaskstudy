from flask import Flask, request, url_for, render_template, redirect, flash
from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import login_user, login_required, logout_user, current_user


app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'

from flask_login import LoginManager
login_manager = LoginManager(app) # 实例化扩展类

@login_manager.user_loader
def load_user(user_id): # 创建用户加载回调函数，接受用户 ID 作为参数
    user = User.query.get(int(user_id)) # 用 ID 作为 User 模型的主键查询对应的用户
    return user # 返回用户对象

#flask 页面
#上下文处理
@app.context_processor
def inject_user():
    user = User.query.first()
    return dict(user = user)

# 主页面
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if not current_user.is_authenticated: # 如果当前用户未认证
            return redirect(url_for('index'))
        title = request.form.get('title')
        year = request.form.get('year')
        if not title or not year or len(year) > 4 or len(title)>60:
            flash('Invalid input.')
            return redirect(url_for('index'))
        movie = Movie(title = title, year=year)
        db.session.add(movie)
        db.session.commit()
        flash('Item created.')
        return redirect(url_for('index'))

    movies = Movie.query.all()
    return render_template('index.html', movies=movies)

#编辑信息
@app.route('/movie/edit/<int:movie_id>',methods=['GET','POST'])
@login_required
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    if request.method == 'POST':
        title = request.form['title']
        year = request.form['year']
        if not title or not year or len(year)>4 or len(title)>60:
            flash('Invalid input')
            return redirect(url_for('edit',movie_id=movie_id))
        movie.title = title
        movie.year = year
        db.session.commit()
        flash('updated')
        return redirect(url_for('index'))
    return render_template('edit.html',movie=movie)

#删除
@app.route('/movie/delete/<int:movie_id>',methods=['POST'])
@login_required
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash('Item deleted')
    return redirect(url_for('index'))

@app.route('/user/<name>')
def user_page(name):
    return 'User: %s' % name

# 错误页面装饰
@app.errorhandler(404)
def page_not_find(e):
    user = User.query.first()
    return render_template('404.html'), 404

# 登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('login'))
        user = User.query.first()
        # 验证用户名和密码是否一致
        if username == user.username and user.validate_password(password):
            login_user(user) # 登入用户
            flash('Login success.')
            return redirect(url_for('index')) # 重定向到主页
        flash('Invalid username or password.') # 如果验证失败，显示错误消息
        return redirect(url_for('login')) # 重定向回登录页面
    return render_template('login.html')
#登出
@app.route('/logout')
@login_required # 用于视图保护，后面会详细介绍
def logout():
    logout_user() # 登出用户
    flash('Goodbye.')
    return redirect(url_for('index')) 

#修改用户名
@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form['name']
        if not name or len(name) > 20:
            flash('Invalid input.')
            return redirect(url_for('settings'))

        current_user.name = name
        db.session.commit()
        flash('Settings updated.')
        return redirect(url_for('index'))
    return render_template('settings.html')

# 数据库主体
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///' + os.path.join(app.root_path, 'data.db')

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    year = db.Column(db.String(4))

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    username = db.Column(db.String(20)) # 用户名
    password_hash = db.Column(db.String(128)) # 密码散列值

    def set_password(self, password): # 用来设置密码的方法，接受密码作为参数
        self.password_hash = generate_password_hash(password) #将生成的密码保持到对应字段
    def validate_password(self, password): # 用于验证密码的方法，接受密码作为参数
        return check_password_hash(self.password_hash, password)

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

@app.cli.command()
@click.option('--username', prompt=True, help='The username used to login.')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password used to login.')
def admin(username, password):
    """Create user."""
    db.create_all()
    user = User.query.first()
    if user is not None:
        click.echo('Updating user...')
        user.username = username
        user.set_password(password) # 设置密码
    else:
        click.echo('Creating user...')
        user = User(username=username, name='Admin')
        user.set_password(password) # 设置密码
        db.session.add(user)
    db.session.commit() # 提交数据库会话
    click.echo('Done.')

login_manager.login_view = 'login'