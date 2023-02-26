from app.shared.models import db


class Period(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))

    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)
    direction = db.Column(db.String)
    diff_days = db.Column(db.Integer)
    count_videos = db.Column(db.Integer)
