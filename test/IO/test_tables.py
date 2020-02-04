from mysrc.IO.my_tables import Base
from mysrc.IO.file_reader import myhost


def test_create_tables():
    from sqlalchemy import create_engine
    url = myhost("test/config.json")
    # url = 'postgresql+psycopg2://postgres:postgres@localhost:3306/postgres'
    engine = create_engine(url)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    assert engine.table_names() == ['charge_network', 'charge_point']