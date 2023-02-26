from flask import jsonify, request

from app import db
from app.tag.models import Tag
from app.tag import tag
from app.tag.serialize import tags_schema


# todo совместное редактирование тегов
@tag.route('/tags', methods=['GET'])
def tags():
    tags = Tag.query.all()
    for tag in tags:
        if not tag.name:
            db.session.delete(tag)
        db.session.commit()
    tags = Tag.query.all()
    return jsonify(tags_schema.dump(tags))


@tag.route('/tag', methods=['PUT', 'DELETE', 'POST'])
def tag():
    if request.method == 'PUT':
        tag = Tag(name='')
        db.session.add(tag)
        db.session.commit()
        return jsonify(tag.id)
    elif request.method == 'DELETE':
        pk = request.json.get('id')
        tag = Tag.query.get(pk)
        db.session.delete(tag)
        db.session.commit()
        return jsonify({"success": "ok"})
    elif request.method == 'POST':
        pk = request.json.get('id')
        name = request.json.get('name')
        tag = Tag.query.get(pk)
        tag.name = name
        db.session.commit()
        return jsonify({"success": "ok"})
