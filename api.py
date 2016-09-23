from flask import Flask, request, jsonify
from apispec import APISpec
from flask_cors import CORS

import database
from models import TodoList
from process_schemas import CreateTodoListInput, CreateTodoListOutput, AddTodoListItemInput, AddTodoListItemOutput

app = Flask(__name__)
CORS(app)

ctx = app.test_request_context()
ctx.push()


spec = APISpec(
    title='Todo',
    version='1.0.0',
    plugins=(
        'apispec.ext.flask',
        'apispec.ext.marshmallow',
    ),
)


spec.definition('CreateTodoListInput', schema=CreateTodoListInput)
spec.definition('CreateTodoListOutput', schema=CreateTodoListOutput)


@app.route('/create-todo-list/', methods=['POST'])
def create_todo_list():
    """Create todo list
    ---
    post:
        parameters:
             - in: 'body'
               name: 'CreateTodoListInput'
               schema:
                    $ref: '#/definitions/CreateTodoListInput'
        responses:
            200:
                schema:
                    $ref: '#/definitions/CreateTodoListOutput'
    """
    create_todo_list_input_schema = CreateTodoListInput()
    create_todo_list_output_schema = CreateTodoListOutput()

    with database.session_scope() as session:
        # This is what a developer should do I guess.

        data, errors = create_todo_list_input_schema.load(request.get_json())

        session.add(data['todo_list'])
        session.commit()

        data, errors = create_todo_list_output_schema.dump({'todo_list': data['todo_list']})

    return jsonify(data)
spec.add_path(view=create_todo_list)


spec.definition('AddTodoListItemInput', schema=AddTodoListItemInput)
spec.definition('AddTodoListItemOutput', schema=AddTodoListItemOutput)


@app.route('/add-item-to-todo-list/', methods=['POST'])
def add_item_to_todo_list():
    """Add item to todo list
    ---
    post:
        parameters:
            - in: 'body'
              name: 'AddTodoListItemInput'
              schema:
                    $ref: '#/definitions/AddTodoListItemInput'
        responses:
            200:
                schema:
                    $ref: '#/definitions/AddTodoListItemOutput'

    """
    add_item_to_todo_list_input_schema = AddTodoListItemInput()
    add_item_to_todo_list_output_schema = AddTodoListItemOutput()

    with database.session_scope() as session:

        data, errors = add_item_to_todo_list_input_schema.load(request.get_json())

        todo_list = session.query(TodoList).filter(TodoList.uuid == data['todo_list']['uuid']).first()
        data['todo_list_item'].todo_list = todo_list

        session.add(data['todo_list_item'])
        session.commit()

        data, errors = add_item_to_todo_list_output_schema.dump({'todo_list_item': data['todo_list_item']})

    return jsonify(data)
spec.add_path(view=add_item_to_todo_list)


@app.route("/spec")
def apispec():
    return jsonify(spec.to_dict())


if __name__ == "__main__":
    app.run()
