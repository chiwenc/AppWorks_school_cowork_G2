from server import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    provider = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(255), index=True, unique=True, nullable=False)
    password = db.Column(db.String(255))
    name = db.Column(db.String(127), nullable=False)
    picture = db.Column(db.String(255))
    access_token = db.Column(db.Text(), nullable=False)
    access_expired = db.Column(db.BigInteger(), nullable=False)

    def __repr__(self):
        return '<User {}, {}, {}>'.format(self.id, self.name, self.email)


def get_user(email):
    try:
        user = User.query.filter_by(email=email).all()
        if user:
            return user[0].to_json()
        else:
            return None
    except Exception as e:
        print(e)
        return None


def get_user_by_name(name):
    try:
        user = User.query.filter_by(name=name).all()
        if user:
            return user[0].to_json()
        else:
            return None
    except Exception as e:
        print(e)
        return None


def create_user(user):
    try:
        new_user = User(**user)
        db.session.add(new_user)
        db.session.commit()
        return new_user.id
    except Exception as e:
        print(e)
        return None