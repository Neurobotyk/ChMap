from sqlalchemy import Table, Column, Integer, BigInteger, Numeric, String, ForeignKey, Float, Text, DateTime
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class ChargeNetwork(Base):
    __tablename__ = 'charge_network'
    needed_list = [ "latitude","longitude","unit_cost","owner","avg_power"]
    id = Column( BigInteger(), primary_key=True)
    latitude = Column(Float(), nullable=False)
    longitude = Column(Float(), nullable=False)
    created_on = Column(DateTime(), default=datetime.now)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now)
    unit_cost  = Column(Float())
    owner = Column(Text(), nullable=False)
    avg_power  = Column(Float())


class ChargePoint(Base):
    __tablename__ = 'charge_point'
    needed_list = [ "power","id_charge_network"]
    id = Column( BigInteger(), primary_key=True)
    power  = Column(Float())
    id_charge_network = Column(ForeignKey('charge_network.id', ondelete='CASCADE'), nullable=False)
    created_on = Column(DateTime(), default=datetime.now)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now)

def create_(engine):
    Base.metadata.create_all(engine)

def drop_(engine):
    Base.metadata.create_all(engine)
    

if __name__ == "__main__":
    from sqlalchemy import create_engine
    url = 'postgresql+psycopg2://postgres:postgres@localhost:5432/chargemap'
    # url = 'postgresql+psycopg2://postgres:postgres@localhost:3306/postgres'
    engine = create_engine(url)    
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    print(engine.table_names())
