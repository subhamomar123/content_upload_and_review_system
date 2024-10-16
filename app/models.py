from app import db


class Movie(db.Model):
    __tablename__ = "movie"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    original_title = db.Column(db.String)  # Add this line
    overview = db.Column(db.Text)
    release_date = db.Column(db.Date)
    budget = db.Column(db.Integer)
    revenue = db.Column(db.Integer)
    runtime = db.Column(db.Integer)
    vote_average = db.Column(db.Float)
    vote_count = db.Column(db.Integer)
    status = db.Column(db.String)
    homepage = db.Column(db.String)
    original_language = db.Column(db.String)
    production_company_id = db.Column(db.Integer)
    genre_id = db.Column(db.Integer)
    languages = db.Column(db.String)  # Store languages as a string

    def __repr__(self):
        return f"<Movie {self.title}>"
