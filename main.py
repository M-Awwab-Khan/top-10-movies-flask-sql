from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, NumberRange
import requests

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
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    ranking: Mapped[int] = mapped_column(Integer, nullable=False)
    review: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)

# CREATE TABLE
db.init_app(app)

with app.app_context():
    db.create_all()

class EditMovie(FlaskForm):
    rating = StringField('Cafe name', validators=[DataRequired(), NumberRange(0, 10)])
    review = StringField('Opening Time e.g. 8AM', validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.route("/")
def home():
    with app.app_context():
        result = db.session.execute(db.select(Movie).order_by(Movie.ranking.desc()))
        all_movies = result.scalars()
        return render_template("index.html", movies=all_movies)

@app.route('/edit/<int:id>')
def edit(id, methods=['POST', 'GET']):
    form = EditMovie()
    return render_template('edit.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
