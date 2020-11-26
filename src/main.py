"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Todo
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/todos', methods=['GET'])
def list_todos():
    todos = Todo.query.all()

    return jsonify(list(map(lambda todo: todo.serialize(), todos))), 200


@app.route('/todos', methods=['POST'])
def create_todo():
    todo_content = request.get_json()

    if todo_content is None:
        raise APIException("You need to specify the request body as a json object", status_code=400)

    if 'done' not in todo_content:
        raise APIException('You need to specify the done setting', status_code=400)

    if 'label' not in todo_content:
        raise APIException('You need to specify the label info', status_code=400)

    todo = Todo(label=todo_content['label'], done=bool(todo_content['done']))
    db.session.add(todo)
    db.session.commit()
    return "ok", 200


@app.route('/todos/<int:id>', methods=['GET'])
def show_todo(id):
    todo = Todo.query.get_or_404(id)

    return jsonify(todo.serialize()), 200

@app.route('/todos/<int:id>', methods=['DELETE'])
def delete_todo(id):
    todo = Todo.query.get_or_404(id)
    db.session.delete(todo)
    db.session.commit()

    return "ok", 200



# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
