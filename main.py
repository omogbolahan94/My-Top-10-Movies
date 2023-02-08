from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
import os

# TMDB API KEY AND URL
API_KEY = os.environ.get('TMDB-KEY')   # '13beef30403918a900d954a0d0816299'
API_URL = 'https://api.themoviedb.org/3/search/movie' # 'https://api.themoviedb.org/3/movie/550?api_key=13beef30403918a900d954a0d0816299'

# FLASK APP
app = Flask('Top10 Movies')

# configure the Bootstrap with the flask app
app.config['SECRET_KEY'] = os.environ.get('TOP10-MOVIE-APP-SECRETE-KEY')   #'8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

# configure the app with SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///top10-movies.db'
db = SQLAlchemy(app)


with app.app_context():
    class MovieForm(FlaskForm):
        title = StringField('Title', validators=[DataRequired()])
        submit = SubmitField('Add Movie')


    class UpdateForm(FlaskForm):
        form_rating = StringField("Your Rating Out of 10 e.g. 7.5", validators=[DataRequired()])
        form_review = StringField("Your Review", validators=[DataRequired()])
        submit = SubmitField("Done")


    class Movie(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(250), unique=True, nullable=False)
        year = db.Column(db.Integer, nullable=False)
        description = db.Column(db.String(500), nullable=False)
        rating = db.Column(db.Float, nullable=True)
        ranking = db.Column(db.Integer, nullable=True)
        review = db.Column(db.String(250), nullable=True)
        img_url = db.Column(db.String(250), nullable=False)

        def __repr__(self):
            movie = f'{self.id} {self.title} {self.rating} {self.review}'
            return movie.split(' ')[0]

    # db.create_all()
    # tablelass

    # new_movie = Movie(
    #     id=1,
    #     title="Phone Booth 1",
    #     year=2002,
    #     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
    #     rating=7.3,
    #     ranking=10,
    #     review="My favourite character was the caller.",
    #     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
    # )

    # db.session.add(new_movie)
    # db.session.commit()


    @app.route("/")
    def home():
        movies = db.session.query(Movie).all()
        return render_template("index.html", all_movies=movies)

    @app.route("/add", methods=['GET', 'POST'])
    def add():
        form = MovieForm()

        if form.validate_on_submit():
            title = form.title.data,
            result = requests.get(API_URL, params={'api_key': API_KEY, 'query': title}).json()
            data = result['results']
            return render_template('select.html', all_movies=data)
        return render_template('add.html', form=form)

    @app.route("/select")
    def select():
        movie_url = 'https://api.themoviedb.org/3/movie'
        img_url = 'https://image.tmdb.org/t/p/w500'
        movie_id = request.args.get('id')
        response = requests.get(f'{movie_url}/{movie_id}', params={"api_key": API_KEY, "language": "en-US"})
        data = response.json()
        new_movie = Movie(
            title=data["title"],
            year=data["release_date"].split("-")[0],
            img_url=f"{img_url}/{data['poster_path']}",
            description=data["overview"]
        )
        db.session.add(new_movie)
        db.session.commit()

        id = Movie.query.filter_by(title=data["title"]).first()  # return id number of the target movie title
        return redirect(url_for('update', id=id))

    @app.route("/update", methods=['GET', 'POST'])
    def update():
        form = UpdateForm()
        movie_id = request.args.get('id')
        selected_movie = Movie.query.get(movie_id)
        if form.validate_on_submit():
            selected_movie.rating = form.form_rating.data
            selected_movie.review = form.form_review.data
            db.session.commit()
            return redirect(url_for('home'))
        return render_template('update.html', selected_movie=selected_movie, form=form)

    @app.route("/delete")
    def delete():
        movie_id = request.args.get('id')
        movie = Movie.query.get(movie_id)
        db.session.delete(movie)
        db.session.commit()
        return redirect(url_for('home'))

    if __name__ == '__main__':
        app.run(debug=True)
        # print(API_KEY)