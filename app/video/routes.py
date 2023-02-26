from flask import jsonify, request
from app.tag.models import Tag
from app.shared.models import db
from app.video.models import Video
from app.video import video
from app.video.serialize import videos_schema


# todo совместное редактирование тегов
@video.route('/videos', methods=['GET'])
def videos():
    session = request.args.get('session')
    count = request.args.get('count')
    task = None
    if not task:
        return jsonify({"error": "задачи не существует"})
    elif count:
        count = int(count)
        videos = Video.query.order_by(Video.id.desc()).limit(count).all()
        videos.reverse()
    else:
        videos = Video.all()
    return jsonify(videos_schema.dump(videos))


# @video.route('/video', methods=['PUT', 'DELETE', 'POST'])
# def video():
#     if request.method == 'PUT':
#         video = Video(name='')
#         db.session.add(video)
#         db.session.commit()
#         return jsonify(video.id)
#     elif request.method == 'DELETE':
#         pk = request.json.get('id')
#         video = Video.query.get(pk)
#         db.session.delete(video)
#         db.session.commit()
#         return jsonify({"success": "ok"})
#     elif request.method == 'POST':
#         pk = request.json.get('id')
#         name = request.json.get('name')
#         video = Video.query.get(pk)
#         video.name = name
#         db.session.commit()
#         return jsonify({"success": "ok"})
@video.route('/video-tag', methods=['PUT', 'DELETE', "POST"])
def video_tag_add():
    if request.method == 'PUT':
        pk = request.json.get('id')
        tag_pk = request.json.get('tagId')
        video = Video.query.get(pk)
        tag = Tag.query.get(tag_pk)
        video.tags.append(tag)
        db.session.commit()
        return jsonify({"success": "ok"})
    elif request.method == 'DELETE':
        pk = request.json.get('id')
        tag_pk = request.json.get('tagId')
        video = Video.query.get(pk)
        tag = Tag.query.get(tag_pk)
        video.tags.remove(tag)
        db.session.commit()
        return jsonify({"success": "ok"})
