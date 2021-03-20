from server import db

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(127), nullable=False)
    item_id = db.Column(db.String(200), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    time = db.Column(db.TIMESTAMP())

class SimilarityModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item1_id = db.Column(db.String(200), nullable=False)
    item2_id = db.Column(db.String(200), nullable=False)
    similarity = db.Column(db.Float, nullable=False)
