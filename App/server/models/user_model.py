from server import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    provider = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(255), index=True, unique=True, nullable=False)
    password = db.Column(db.String(255))
    username = db.Column(db.String(127), nullable=False)
    picture = db.Column(db.String(255))
    access_token = db.Column(db.Text(), nullable=False)
    access_expire = db.Column(db.BigInteger(), nullable=False)
    login_at = db.Column(db.TIMESTAMP())

    def __init__(self, model_dict):
        self.__dict__.update(model_dict)

    def __repr__(self):
        return '<User {}, {}, {}>'.format(self.id, self.username, self.email)

def get_user(email):
    user = User.query.filter_by(email = email).all()
    if user:
        return user[0].to_json()
    else:
        return None

def create_user(user):
    new_user = User(user)
    db.session.add(new_user)
    db.session.commit()
    return new_user.id