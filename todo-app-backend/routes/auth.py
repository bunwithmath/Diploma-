import datetime
import jwt
from flask import Blueprint, request, jsonify, abort, current_app
from models import db, User
from utils import hash_password, check_password

auth_blueprint = Blueprint('auth', __name__)

def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }
    token = jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')
    return token

def verify_token(token):
    try:
        payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        abort(401, description="Expired token")
    except jwt.InvalidTokenError:
        abort(401, description="Invalid token")

@auth_blueprint.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        abort(400, description="Invalid JSON data")

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        abort(400, description="Username and password are required")

    if User.query.filter_by(username=username).first():
        abort(400, description="User already exists")

    new_user = User(username=username, password=hash_password(password))
    db.session.add(new_user)
    db.session.commit()

    token = generate_token(new_user.id)
    return token, 201  # Возвращаем токен как строку

@auth_blueprint.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        abort(400, description="Invalid JSON data")

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        abort(400, description="Username and password are required")

    user = User.query.filter_by(username=username).first()
    if not user or not check_password(user.password, password):
        abort(401, description="Invalid credentials")

    token = generate_token(user.id)
    return token, 200  # Возвращаем токен как строку
