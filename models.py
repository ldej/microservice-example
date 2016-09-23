import datetime
import uuid

from sqlalchemy import Column, String, DateTime, ForeignKeyConstraint, Numeric, Boolean
from sqlalchemy import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy_utils import UUIDType, aggregated

Base = declarative_base()


class TodoList(Base):
    __tablename__ = 'todo_list'

    uuid = Column(UUIDType, primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    is_created_at = Column(DateTime(timezone=True), default=datetime.datetime.now, nullable=False)

    @aggregated('todo_list_items', Column(Numeric))
    def todo_list_item_count(self):
        return func.count('1')

    __table_args__ = (
    )

    def __init__(self, name=None, is_created_at=None, todo_list_items=None):
        super(TodoList, self).__init__()
        self.name = name
        self.is_created_at = is_created_at
        self.todo_list_items = todo_list_items


class TodoListItem(Base):
    __tablename__ = 'todo_list_item'

    uuid = Column(UUIDType, primary_key=True, default=uuid.uuid4)
    text = Column(String, nullable=False)
    checked = Column(Boolean, default=False, nullable=False)
    todo_list_uuid = Column(UUIDType, nullable=False)
    todo_list = relationship(TodoList, backref=backref('todo_list_items'), foreign_keys=[todo_list_uuid])
    is_created_at = Column(DateTime(timezone=True), default=datetime.datetime.now, nullable=False)

    __table_args__ = (
        ForeignKeyConstraint([todo_list_uuid], [TodoList.uuid]),
    )

    def __init__(self, text=None, todo_list=None, is_created_at=None, checked=None):
        super(TodoListItem, self).__init__()
        self.checked = checked
        self.text = text
        self.todo_list = todo_list
        self.is_created_at = is_created_at
