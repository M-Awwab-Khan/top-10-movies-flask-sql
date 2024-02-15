from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired
import requests

TMDB_BASE_URL = 'https://api.themoviedb.org/3/search/movie'
TMDB_MORE_INFO = 'https://api.themoviedb.org/3/movie'
TMDB_AUTH_TOKEN = 'eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI3NTQzNjA5NWIwNjFmNGI2MjMwNjk2ZjcwZDUzNjE5NyIsInN1YiI6IjY0M2JlNmIxOGVjNGFiMDRlZWFlZTYxNCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.ZKpwarjv4C5n_WvHadA0OWGNTFsT7gQMDjx4Lgt64IA'

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///Movies.db"
Bootstrap5(app)

# CREATE DB
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class Movie(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String(250), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=True)
    ranking: Mapped[int] = mapped_column(Integer, nullable=True)
    review: Mapped[str] = mapped_column(String(250), nullable=True)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)

# CREATE TABLE
db.init_app(app)

with app.app_context():
    db.create_all()

class EditMovie(FlaskForm):
    rating = FloatField('Your rating out of 10 e.g 7.5', validators=[DataRequired()])
    review = StringField('Your review', validators=[DataRequired()])
    submit = SubmitField('Update')

class AddMovie(FlaskForm):
    title = StringField('Movie Title', validators=[DataRequired()])
    submit = SubmitField('Search')


@app.route("/")
def home():
    with app.app_context():
        result = db.session.execute(db.select(Movie).order_by(Movie.ranking.desc()))
        all_movies = result.scalars()
        return render_template("index.html", movies=all_movies)

@app.route('/edit/<int:id>', methods=['POST', 'GET'])
def edit(id):
    form = EditMovie()
    movie_to_update = db.get_or_404(Movie, id)
    if form.validate_on_submit():           
            movie_to_update.rating = float(form.rating.data)
            movie_to_update.review = form.review.data
            db.session.commit()
            return redirect('/')
    return render_template('edit.html', form=form)

@app.route('/delete/<int:id>')
def delete(id):
    with app.app_context():
        movie_to_delete = db.session.execute(db.select(Movie).where(Movie.id == id)).scalar()
        # or movie_to_delete = db.get_or_404(movie, id)
        db.session.delete(movie_to_delete)
        db.session.commit()
        return redirect('/')

@app.route('/add', methods=['POST', 'GET'])
def add():
    form = AddMovie()
    if form.validate_on_submit():
        headers = {
            "accept": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI3NTQzNjA5NWIwNjFmNGI2MjMwNjk2ZjcwZDUzNjE5NyIsInN1YiI6IjY0M2JlNmIxOGVjNGFiMDRlZWFlZTYxNCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.ZKpwarjv4C5n_WvHadA0OWGNTFsT7gQMDjx4Lgt64IA"
        }
        params = {
            'query': form.title.data
        }
        response = requests.get(TMDB_BASE_URL, params=params, headers=headers)
        movies = response.json()['results']
        return render_template('select.html', movies=movies)
    return render_template('add.html', form=form)

@app.route('/movie/<int:id>')
def create(id):
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI3NTQzNjA5NWIwNjFmNGI2MjMwNjk2ZjcwZDUzNjE5NyIsInN1YiI6IjY0M2JlNmIxOGVjNGFiMDRlZWFlZTYxNCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.ZKpwarjv4C5n_WvHadA0OWGNTFsT7gQMDjx4Lgt64IA"
    }
    response = requests.get(f"{TMDB_MORE_INFO}/{id}", headers=headers)
    movie = response.json()
    print(movie)
    new_movie = Movie(
        title=movie['title'],
        year=movie['release_date'].split('-')[0],
        description=movie['overview'],
        img_url=f"https://image.tmdb.org/t/p/w500{movie['poster_path']}",
    )
    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for('edit', id=id))
    

if __name__ == '__main__':
    app.run(debug=True)
