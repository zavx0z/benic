from app.shared.models import db

association_table = db.Table(
    'video_tags', db.Model.metadata,
    db.Column('video_id', db.Integer, db.ForeignKey('video.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
)


class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
    tags = db.relationship("Tag", secondary=association_table, backref=db.backref('videos', lazy='dynamic'))

    channel = db.Column(db.String)
    name = db.Column(db.String)
    link = db.Column(db.String)
    views = db.Column(db.Integer)
    date = db.Column(db.String)
    duration = db.Column(db.String)
