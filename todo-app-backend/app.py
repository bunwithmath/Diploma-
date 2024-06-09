from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from models import db, User, Task, Performer, Subtask
from config import Config
from routes.auth import auth_blueprint
from routes.tasks import tasks_blueprint
from routes.performers import performers_blueprint

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

db.init_app(app)
migrate = Migrate(app, db)

app.register_blueprint(auth_blueprint, url_prefix='/auth')
app.register_blueprint(tasks_blueprint, url_prefix='/tasks')
app.register_blueprint(performers_blueprint, url_prefix='/performers')

# Глобальные обработчики ошибок
@app.errorhandler(Exception)
def handle_exception(e):
    response = {
        "error": str(e),
        "description": e.description if hasattr(e, 'description') else 'An error occurred'
    }
    return jsonify(response), e.code if hasattr(e, 'code') else 500

@app.errorhandler(400)
def bad_request(e):
    return jsonify(error=str(e), description='Bad request'), 400

@app.errorhandler(401)
def unauthorized(e):
    return jsonify(error=str(e), description='Unauthorized'), 401

@app.errorhandler(404)
def not_found(e):
    return jsonify(error=str(e), description='Resource not found'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return jsonify(error=str(e), description='Internal server error'), 500

if __name__ == '__main__':
    app.run(debug=True)
