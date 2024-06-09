from flask import Blueprint, request, jsonify, abort, current_app
from routes.auth import verify_token
from models import db, Task, Subtask, Performer
import logging

tasks_blueprint = Blueprint('tasks', __name__)

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

@tasks_blueprint.route('/<task_id>/done', methods=['PATCH'])
def update_task_is_done(task_id):
    try:
        user_id = get_user_id_from_token()

        task = Task.query.get(task_id)
        if not task:
            current_app.logger.error(f"Task not found: {task_id}")
            abort(404, description="Task not found")
        if task.user_id != user_id:
            current_app.logger.error(f"Unauthorized access for task: {task_id}")
            abort(403, description="Unauthorized access")

        task.is_done = not task.is_done  # Переключение статуса
        db.session.commit()

        # Для отладки: проверим, что статус действительно изменился
        updated_task = Task.query.get(task_id)
        current_app.logger.debug(f"Updated task status: {updated_task.is_done}")

        return jsonify({'message': 'Task updated successfully'}), 200
    except Exception as e:
        current_app.logger.error(f"Error in update_task_is_done: {e}")
        abort(500, description="An error occurred while updating task")

@tasks_blueprint.route('/', methods=['POST'])
def create_task():
    try:
        user_id = get_user_id_from_token()
        data = request.get_json()
        deadline_str = data.get('deadline')

        performer_id = data.get('performer_id')
        performer = Performer.query.get(performer_id) if performer_id else None
        current_app.logger.debug(f"Performer ID: {performer_id}, Performer: {performer}")

        task = Task(
            id=data['id'],
            title=data['title'],
            description=data.get('description'),
            is_done=False,  # Новая задача по умолчанию не завершена
            deadline=deadline_str,
            user_id=user_id,
            performer=performer
        )
        db.session.add(task)
        db.session.commit()

        for subtask_data in data.get('subtasks', []):
            subtask = Subtask(
                id=subtask_data['id'],
                title=subtask_data['title'],
                is_done=subtask_data['isDone'],
                task_id=task.id
            )
            db.session.add(subtask)

        db.session.commit()
        return jsonify({'message': 'Task created successfully'}), 201
    except Exception as e:
        current_app.logger.error(f"Error in create_task: {e}")
        current_app.logger.error(e, exc_info=True)  # Вывод полного стека ошибки
        abort(500, description="An error occurred while creating task")

@tasks_blueprint.route('/', methods=['GET'])
def get_tasks():
    try:
        user_id = get_user_id_from_token()
        tasks = Task.query.filter_by(user_id=user_id).all()

        result = []
        for task in tasks:
            current_app.logger.debug(f"Processing task: {task.id}, deadline: {task.deadline}, is_done: {task.is_done}")
            result.append(task.to_dict())

        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_tasks: {e}")
        current_app.logger.error(e, exc_info=True)  # Вывод полного стека ошибки
        abort(500, description="An error occurred while fetching tasks")

@tasks_blueprint.route('/<task_id>', methods=['GET'])
def get_task(task_id):
    try:
        user_id = get_user_id_from_token()
        task = Task.query.get(task_id)

        if not task or task.user_id != user_id:
            abort(404, description="Task not found")

        return jsonify(task.to_dict()), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_task: {e}")
        current_app.logger.error(e, exc_info=True)  # Вывод полного стека ошибки
        abort(500, description="An error occurred while fetching task")

@tasks_blueprint.route('/<task_id>', methods=['PUT'])
def update_task(task_id):
    try:
        user_id = get_user_id_from_token()
        data = request.get_json()
        task = Task.query.get(task_id)

        if not task or task.user_id != user_id:
            abort(404, description="Task not found")

        performer_id = data.get('performer_id')
        performer = Performer.query.get(performer_id) if performer_id else None
        current_app.logger.debug(f"Updating task with Performer ID: {performer_id}, Performer: {performer}")

        task.title = data.get('title', task.title)
        task.description = data.get('description', task.description)
        task.is_done = data.get('isDone', task.is_done)
        task.deadline = data.get('deadline')
        task.performer = performer

        if 'subtasks' in data:
            for subtask_data in data['subtasks']:
                subtask = Subtask.query.get(subtask_data['id'])
                if subtask:
                    subtask.title = subtask_data.get('title', subtask.title)
                    subtask.is_done = subtask_data.get('isDone', subtask.is_done)
                else:
                    new_subtask = Subtask(
                        id=subtask_data['id'],
                        title=subtask_data['title'],
                        is_done=subtask_data['isDone'],
                        task_id=task.id
                    )
                    db.session.add(new_subtask)

        db.session.commit()
        return jsonify({'message': 'Task updated successfully'}), 200
    except Exception as e:
        current_app.logger.error(f"Error in update_task: {e}")
        current_app.logger.error(e, exc_info=True)  # Вывод полного стека ошибки
        abort(500, description="An error occurred while updating task")


@tasks_blueprint.route('/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    try:
        user_id = get_user_id_from_token()
        task = Task.query.get(task_id)

        if not task or task.user_id != user_id:
            abort(404, description="Task not found")

        db.session.delete(task)
        db.session.commit()
        return jsonify({'message': 'Task deleted successfully'}), 200
    except Exception as e:
        current_app.logger.error(f"Error in delete_task: {e}")
        current_app.logger.error(e, exc_info=True)  # Вывод полного стека ошибки
        abort(500, description="An error occurred while deleting task")
