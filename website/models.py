from datetime import datetime

from sqlalchemy import DateTime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from website import db, login_manager


class user_tbl(UserMixin, db.Model):
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(50))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(1))
    location = db.Column(db.String(40))
    isAdmin = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f"User('{self.username}')"

    def set_password(self, passw):
        self.password = generate_password_hash(passw)

    def verify_password(self, passw):
        return check_password_hash(self.password, passw)

    def get_id(self):
        return self.user_id


@login_manager.user_loader
def load_user(user_id):
    return user_tbl.query.get(int(user_id))


class media_tbl(db.Model):
    __table_args__ = {"extend_existing": True}
    media_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    media_desc = db.Column(db.String(100))
    media_image_0 = db.Column(db.LargeBinary(length=200000))
    media_image_1 = db.Column(db.LargeBinary(length=200000))
    media_image_2 = db.Column(db.LargeBinary(length=200000))
    media_image_3 = db.Column(db.LargeBinary(length=200000))
    media_post_time = db.Column(DateTime, default=datetime.now)
    media_user_id = db.Column(db.Integer, db.ForeignKey('user_tbl.user_id'), nullable=False)
    place_owner_user_id = db.Column(db.Integer, db.ForeignKey('user_tbl.user_id'), nullable=False)
    comments = db.relationship('comment_tbl', backref='title', lazy='dynamic')

    media_img_num = db.Column(db.Integer)

    def __unicode__(self):
        return self.media_id


class friend_tbl(db.Model):
    uid = db.Column(db.Integer, db.ForeignKey('user_tbl.user_id'), primary_key=True, nullable=False)
    fid = db.Column(db.Integer, db.ForeignKey('user_tbl.user_id'), primary_key=True, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    user_action = db.Column(db.Integer, nullable=False)


class visibility_tbl(db.Model):
    vis_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.Integer, db.ForeignKey('media_tbl.media_id'), nullable=False)
    block_id = db.Column(db.Integer)


class comment_tbl(db.Model):
    comment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.Integer, db.ForeignKey('media_tbl.media_id'))
    comment_description = db.Column(db.String(100))
    user_id = db.column = db.Column(db.Integer)
    comment_time = db.Column(DateTime, default=datetime.now)

class message_tbl(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user_tbl.user_id'))
    receive_id = db.Column(db.Integer, db.ForeignKey('user_tbl.user_id'))
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Message {}>'.format(self.body)


# db.create_all()
