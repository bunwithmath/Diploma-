from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    tasks = db.relationship('Task', back_populates='user')

class Performer(db.Model):
    id = db.Column(db.String, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    middle_name = db.Column(db.String(80), nullable=True)
    birth_date = db.Column(db.String, nullable=True)
    tasks = db.relationship('Task', back_populates='performer')

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'middle_name': self.middle_name,
            'birth_date': self.birth_date
        }

class Subtask(db.Model):
    id = db.Column(db.String, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    is_done = db.Column(db.Boolean, default=False, nullable=False)
    task_id = db.Column(db.String, db.ForeignKey('task.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'is_done': self.is_done,
            'task_id': self.task_id
        }

class Task(db.Model):
    id = db.Column(db.String(80), primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500))
    is_done = db.Column(db.Boolean, nullable=False)
    deadline = db.Column(db.String(100), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    performer_id = db.Column(db.String(80), db.ForeignKey('performer.id'), nullable=True)
    user = db.relationship('User', back_populates='tasks')
    performer = db.relationship('Performer', back_populates='tasks')
    subtasks = db.relationship('Subtask', backref='task', lazy=True)

    def to_dict(self):
        performer_dict = {
            'id': self.performer.id,
            'first_name': self.performer.first_name,
            'last_name': self.performer.last_name,
            'middle_name': self.performer.middle_name,
        } if self.performer else None

        subtasks_list = [{
            'id': subtask.id,
            'title': subtask.title,
            'is_done': subtask.is_done
        } for subtask in self.subtasks]

        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'is_done': self.is_done,
            'deadline': self.deadline,
            'performer': performer_dict,
            'subtasks': subtasks_list
        }