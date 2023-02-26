import datetime
import enum

from app.shared.models import db


# https://stackoverflow.com/questions/37848815/sqlalchemy-postgresql-enum-does-not-create-type-on-db-migrate
class VariantTask(enum.Enum):
    statistic = 'statistic'
    tagging = 'tagging'


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session = db.Column(db.String(128), index=True, unique=True, nullable=True)
    query_string = db.Column(db.String, nullable=False)

    status = db.Column(db.String(128), default='run')
    started = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    completed = db.Column(db.DateTime, nullable=True)
    variant = db.Column(db.Enum(VariantTask))
    interactive = db.Column(db.Boolean(), default=False, nullable=False)

    periods = db.relationship("Period", backref='task', cascade="delete")
    videos = db.relationship("Video", backref='task', cascade='delete')

    @staticmethod
    def add(query, variant, interactive):
        task = Task(query_string=query)
        for item in VariantTask:
            if item.name == variant:
                task.variant = item
                break
        task.interactive = interactive
        db.session.add(task)
        db.session.commit()

    def __repr__(self):
        return f'<Task {self.session}>'
