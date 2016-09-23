from marshmallow import fields
from marshmallow_sqlalchemy import ModelSchema

from models import TodoListItem, TodoList
import database


class TodoListSchema(ModelSchema):
    todo_list_items = fields.Nested('TodoListItemSchema', many=True, exclude=('todo_list',))

    class Meta:
        model = TodoList
        sqla_session = database.session_scope


class TodoListItemSchema(ModelSchema):
    todo_list = fields.Nested('TodoListSchema', exclude=('todo_list_items',))

    class Meta:
        model = TodoListItem
        sqla_session = database.session_scope
