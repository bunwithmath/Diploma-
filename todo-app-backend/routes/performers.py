from flask import Blueprint, request, jsonify, abort, current_app
from routes.auth import verify_token
from models import db, Performer
import logging

performers_blueprint = Blueprint('performers', __name__)

# Установим уровень логирования на DEBUG
logging.basicConfig(level=logging.DEBUG)

def get_user_id_from_token():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        current_app.logger.debug("Missing or invalid Authorization header")
        abort(401, description="Missing or invalid Authorization header")
    token = auth_header.split(' ')[1]
    user_id = verify_token(token)
    if not user_id:
        current_app.logger.debug("Invalid token")
        abort(401, description="Invalid token")
    return user_id

@performers_blueprint.route('/', methods=['GET'])
def get_performers():
    try:
        user_id = get_user_id_from_token()
        performers = Performer.query.all()

        result = []
        for performer in performers:
            performer_data = {
                'id': performer.id,
                'first_name': performer.first_name,
                'last_name': performer.last_name,
                'middle_name': performer.middle_name,
                'birth_date': performer.birth_date
            }
            result.append(performer_data)

        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_performers: {e}")
        abort(500, description="An error occurred while fetching performers")

@performers_blueprint.route('/', methods=['POST'])
def create_performer():
    try:
        user_id = get_user_id_from_token()
        data = request.get_json()

        performer = Performer(
            id=data['id'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            middle_name=data.get('middle_name'),
            birth_date=data.get('birth_date')
        )
        db.session.add(performer)
        db.session.commit()

        return jsonify({'message': 'Performer created successfully'}), 201
    except Exception as e:
        current_app.logger.error(f"Error in create_performer: {e}")
        abort(500, description="An error occurred while creating performer")

@performers_blueprint.route('/<performer_id>', methods=['GET'])
def get_performer(performer_id):
    try:
        user_id = get_user_id_from_token()
        performer = Performer.query.get(performer_id)

        if not performer:
            abort(404, description="Performer not found")

        return jsonify({
            'id': performer.id,
            'first_name': performer.first_name,
            'last_name': performer.last_name,
            'middle_name': performer.middle_name,
            'birth_date': performer.birth_date
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_performer: {e}")
        abort(500, description="An error occurred while fetching performer")

@performers_blueprint.route('/<performer_id>', methods=['PUT'])
def update_performer(performer_id):
    try:
        user_id = get_user_id_from_token()
        data = request.get_json()
        performer = Performer.query.get(performer_id)

        if not performer:
            abort(404, description="Performer not found")

        performer.first_name = data.get('first_name', performer.first_name)
        performer.last_name = data.get('last_name', performer.last_name)
        performer.middle_name = data.get('middle_name', performer.middle_name)
        performer.birth_date = data.get('birth_date', performer.birth_date)

        db.session.commit()
        return jsonify({'message': 'Performer updated successfully'}), 200
    except Exception as e:
        current_app.logger.error(f"Error in update_performer: {e}")
        abort(500, description="An error occurred while updating performer")

@performers_blueprint.route('/<performer_id>', methods=['DELETE'])
def delete_performer(performer_id):
    try:
        user_id = get_user_id_from_token()
        performer = Performer.query.get(performer_id)

        if not performer:
            abort(404, description="Performer not found")

        db.session.delete(performer)
        db.session.commit()
        return jsonify({'message': 'Performer deleted successfully'}), 200
    except Exception as e:
        current_app.logger.error(f"Error in delete_performer: {e}")
        abort(500, description="An error occurred while deleting performer")
