from marshmallow import Schema
from marshmallow import fields

from model_schemas import TodoListSchema, TodoListItemSchema


class CreateTodoListInput(Schema):
    todo_list = fields.Nested(TodoListSchema, only=('name', 'todo_list_items.text',))


class CreateTodoListOutput(Schema):
    todo_list = fields.Nested(TodoListSchema)


class AddTodoListItemInput(Schema):
    todo_list_item = fields.Nested(TodoListItemSchema, only=('uuid',))
    todo_list = fields.Nested(TodoListSchema, only=('uuid',))


class AddTodoListItemOutput(Schema):
    todo_list_item = fields.Nested(TodoListItemSchema)
