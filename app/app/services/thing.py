import logging
from microservice.rpc import rpc

from app import database
from app.models import Thing
from app.schemas import thing_schema, create_thing_schema


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


class ThingService:
    name = 'thing_service'

    @rpc
    async def create_thing(self, *args, **kwargs) -> ([], {}):
        with database.session_scope() as session:
            thing, errors = create_thing_schema.load(kwargs, session=session)
            logger.debug(errors)

            session.add(thing)
            session.flush()

            data, errors = thing_schema.dump(thing)
        return [], data

    @rpc
    async def get_things(self) -> ([], {}):
        with database.session_scope() as session:
            things = session.query(Thing).all()

            things = [thing_schema.dump(thing).data for thing in things]
        return things, {}
