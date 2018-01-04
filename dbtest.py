from sqlalchemy import *
from sqlalchemy.dialects import postgresql

db = create_engine('postgresql://kathrin:password@localhost:5433/gamepicker')
metadata = MetaData(db)

games = Table('games', metadata,
    Column('gid', Integer, primary_key=True),
    Column('name', String(40)),
    Column('max_player', Integer),
    Column('best_playnum', postgresql.ARRAY(Integer))
)
games.create()

i = games.insert()
i.execute(name='Marco Polo', max_player=30, best_playnum=[3, 4, 5])
i.execute({'name': 'John', 'max_player': 42},
          {'name': 'Susan', 'max_player': 57},
          {'name': 'Carl', 'max_player': 33})