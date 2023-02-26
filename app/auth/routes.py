from flask import request, jsonify, g
from flask_cors import cross_origin
from app import db, auth
from app.auth import authenticate
from app.auth.models import User


@auth.verify_password
def verify_password(login_or_token, password):
    user = User.verify_auth_token(login_or_token)
    if not user:
        user = User.query.filter_by(login=login_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


@authenticate.route('/token')
@auth.login_required
@cross_origin()
def get_auth_token():
    user = g.user
    token, expiration = user.generate_auth_token()
    data = {
        "token": token,
        "expiration": expiration,
        "user": {"id": user.id, "login": user.login}
    }
    return jsonify(data)


@authenticate.route('/join', methods=['POST'])
@cross_origin()
def join():
    password = request.json.get('password')
    login = request.json.get('login')
    if not isinstance(password, str) or not isinstance(login, str):
        return jsonify({"error": "не правильный тип данных"}), 500
    if User.query.filter_by(login=login).first() is not None:
        return jsonify({'error': f"Пользователь с логином: {login} уже зарегистрирован!"})
    else:
        user = User(login=login)
        user.hash_password(password)
        db.session.add(user)
        db.session.commit()
        token, expiration = user.generate_auth_token()
        data = {
            "token": token,
            "expiration": expiration,
            "user": {"id": user.id, "login": user.login}
        }
        return jsonify(data)


@authenticate.route('/login')
@auth.login_required
@cross_origin()
def log_in():
    user = g.user
    token, expiration = user.generate_auth_token()
    data = {
        "token": token,
        "expiration": expiration,
        "user": {"id": user.id, "login": user.login}
    }
    return jsonify(data)
