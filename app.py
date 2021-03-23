from flask import Flask, request, url_for, render_template, redirect, flash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'
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




