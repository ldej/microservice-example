import datetime
import uuid

from sqlalchemy import Column, String, DateTime, ForeignKeyConstraint, Numeric, Boolean
from sqlalchemy import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy_utils import UUIDType, aggregated

Base = declarative_base()


class Thing(Base):
    __tablename__ = 'thing'

    uuid = Column(UUIDType, primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    is_created_at = Column(DateTime(timezone=True), default=datetime.datetime.now, nullable=False)

    __table_args__ = (
    )

    def __init__(self, name=None):
        super(Thing, self).__init__()
        self.name = name
