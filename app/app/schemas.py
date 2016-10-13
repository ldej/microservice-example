from marshmallow_sqlalchemy import ModelSchema

from app.models import Thing


class ThingSchema(ModelSchema):
    class Meta:
        model = Thing

thing_schema = ThingSchema()
create_thing_schema = ThingSchema(only=('name',))
