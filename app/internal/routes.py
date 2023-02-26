from datetime import datetime
import os
from flask import request, jsonify
from flask_socketio import emit
from app import db
from app.internal import internal
from app.period.serialize import period_schema
from app.task.models import Task
from app.period.models import Period
from app.video.models import Video
from app.video.serialize import video_schema

HOST = os.getenv("HOST")


@internal.route('/get_status', methods=['POST'])
def get_status():
    session = request.json.get('session')
    task = Task.query.filter_by(session=session).first()
    return jsonify({"status": task.status})


@internal.route('/start', methods=['POST'])
def start():
    session = request.json.get('session')
    q = request.json.get('query')

    task = Task.query.filter_by(query_string=q).first()
    task.session = session
    db.session.commit()

    emit('task', {"status": 'run', "session": session}, namespace='/', broadcast=True)
    return jsonify({"success": "ok"})


@internal.route('/pause', methods=['POST'])
def pause():
    session = request.json.get('session')
    emit('task', {"status": 'pause', "session": session}, namespace='/', broadcast=True)
    return jsonify({"success": "ok"})


@internal.route('/run', methods=['POST'])
def run():
    session = request.json.get('session')
    emit('task', {"status": 'run', "session": session}, namespace='/', broadcast=True)
    return jsonify({"success": "ok"})


@internal.route('/video', methods=['POST'])
def video():
    session = request.json.get("session")
    name = request.json.get('name')
    channel = request.json.get('channel')
    link = request.json.get('link')

    exist = Video.query.filter_by(link=link).all()
    task = Task.query.filter_by(session=session).first()
    if not exist:
        video = Video(
            channel=channel,
            name=name,
            views=request.json.get('views'),
            link=link,
            date=request.json.get('date'),
            duration=request.json.get('duration')
        )
        db.session.add(video)
        task.videos.append(video)
        db.session.commit()
        emit('video', video_schema.dump(video), namespace='/', broadcast=True)
    return jsonify({"status": task.status})


@internal.route('/videos_internal', methods=['POST'])
def videos_internal():
    emit('pageData', request.json, namespace='/', broadcast=True)
    return jsonify({"success": "ok"})


@internal.route('/period', methods=['POST'])
def period():
    session = request.json.get("session")
    task = Task.query.filter_by(session=session).first()
    period = Period(
        start_date=datetime.strptime(request.json.get("start_period"), "%Y/%m/%d"),
        end_date=datetime.strptime(request.json.get("end_period"), "%Y/%m/%d"),
        direction=request.json.get("direction"),
        diff_days=request.json.get("diff_days"),
        count_videos=request.json.get("count_videos")
    )
    db.session.add(period)
    task.periods.append(period)
    db.session.commit()
    emit('period', period_schema.dump(period), namespace='/', broadcast=True)
    return jsonify({"success": "ok"})
