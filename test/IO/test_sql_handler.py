import pytest
from mysrc.IO.file_reader import myhost
from mysrc.IO.my_tables import ChargeNetwork, ChargePoint
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from mysrc.IO.sql_handler import iohandler, Base
from copy import deepcopy


example_data = {
    "network":{
        "id":1,
        "latitude":30,
        "longitude":30,
        "unit_cost":55.345,
        "owner":"Meh",
        "avg_power":"80.567573552"
    }, "point":{
        "power":50,
        "id_charge_network":1
    }
}

@pytest.fixture(scope='session')
def host():
    return myhost("test/config.json")

@pytest.fixture(scope='session')
def engine(host):
    return create_engine(host)

@pytest.fixture(scope='session')
def tabs(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    try:
        yield 
    finally:
        Base.metadata.drop_all(engine)

@pytest.fixture
def dbsession(engine, tabs):
    """Returns an sqlalchemy session, and after the test tears down everything properly."""
    connection = engine.connect()
    # begin the nested transaction
    transaction = connection.begin()
    # use the connection with the already started transaction
    session = Session(bind=connection)
    try:
        yield session
    finally:
        session.close()
        # roll back the broader transaction
        transaction.rollback()
        # put back the connection to the connection pool
        connection.close()
   
@pytest.fixture
def ioh(dbsession):
    return iohandler(dbsession)

def test_insert_network_throw(ioh):
    network={
        # "latitude":30,
        # "longitude":30,
        # "unit_cost":55.345,
        "owner":"Meh",
        "avg_power":"80.567573552"
    }
    ioh = iohandler(dbsession)
    with pytest.raises(Exception) as excinfo:
        ioh.insert_network(network) 
    assert 'missing values of' in excinfo.value.args[0]

def test_insert_network_propper(ioh):
    ins = ioh.insert_network(example_data["network"]) 
    assert ins.updated_on is not None

def test_insert_point_throw(ioh):
    point={
        # "power":50,
        "id_charge_network":1
    }
    ioh = iohandler(dbsession)
    with pytest.raises(Exception) as excinfo:
        ioh.insert_point(point) 
    assert 'missing values of' in excinfo.value.args[0]

def test_insert_point_without_foregin_key(ioh):
    with pytest.raises(Exception) as excinfo:
        ioh.insert_point(example_data["point"])
    assert 'No parent Network' in excinfo.value.args[0]

def test_insert_point_propper(ioh):
    ins= ioh.insert_network(example_data["network"]) 
    assert ins.updated_on is not None
    ins_p = ioh.insert_point(example_data["point"])
    assert ins_p.updated_on is not None

def test_insert__multiple_point_propper(ioh):
    ins= ioh.insert_network(example_data["network"]) 
    assert ins.updated_on is not None
    ins_p = ioh.insert_point(example_data["point"])
    assert ins_p.updated_on is not None
    ins_1 = ioh.insert_point(example_data["point"])
    assert ins_p.updated_on is not None
    assert ins_p.updated_on !=ins_1.updated_on
    ins_2 = ioh.insert_point(example_data["point"])
    assert ins_p.updated_on is not None
    assert ins_p.updated_on !=ins_2.updated_on
    ins_3 = ioh.insert_point(example_data["point"])
    assert ins_p.updated_on is not None
    assert ins_p.updated_on !=ins_3.updated_on


# def test_insert_network_unique_ID(ioh):
#     ins= ioh.insert_network(example_data["network"]) 
#     with pytest.raises(Exception) as excinfo:
#         ioh.insert_network(example_data["network"]) 
#     assert "conflicts with persistent instance" in excinfo.value.args[0]

def test_update_network_if_no(ioh):
    sel = ioh.select_network(example_data["network"]["id"])
    assert sel is None
    with pytest.raises(Exception) as excinfo:
        ioh.update_network(example_data["network"])
    assert 'no network with id' in excinfo.value.args[0]


def test_update_point_if_no(ioh):
    point = deepcopy(example_data["point"])
    point["id"]=1
    sel = ioh.select_point(point["id"])
    assert sel is None
    with pytest.raises(Exception) as excinfo:
        ioh.update_point(point)
    assert 'no point with id' in excinfo.value.args[0]


def test_update_point_propper(ioh):
    ins= ioh.insert_network(example_data["network"]) 
    assert ins.updated_on is not None
    ins_p = ioh.insert_point(example_data["point"])
    point = deepcopy(example_data["point"])
    point["id"]=ins_p.id
    point["power"]="234"
    update = ioh.update_point(point).power
    assert update==234.0

def test_update_network_propper(ioh):
    network = deepcopy(example_data["network"])
    prevowner = network["owner"]
    ins= ioh.insert_network(network) 
    inref = deepcopy(ins)
    network["owner"]= "moi"
    up = ioh.update_network(network)
    sel = ioh.select_network(ins.id)
    assert prevowner!=sel.owner
    assert sel.owner=="moi"

def test_update_abit_network(ioh):
    network = deepcopy(example_data["network"])
    prevowner = network["owner"]
    ins= ioh.insert_network(example_data["network"]) 
    inref = deepcopy(ins)
    n2 = {"id":example_data["network"]["id"],
        "owner":"moi"
    }
    up = ioh.update_network(n2)
    sel = ioh.select_network(ins.id)
    assert prevowner!=sel.owner

def test_select_Point(ioh):
    ins1= ioh.insert_network(example_data["network"]) 
    ins = ioh.insert_point(example_data["point"])
    sel = ioh.select_point(ins.id)
    assert ins==sel

def test_select_point_after_multi_insert(ioh):
    ins_n= ioh.insert_network(example_data["network"]) 
    ins1 = ioh.insert_point(example_data["point"])
    ins2 = ioh.insert_point(example_data["point"])
    sel = ioh.select_point(ins1.id)
    assert ins1==sel
    sel = ioh.select_point(ins2.id)
    assert ins2==sel

def test_select_point_by_network(ioh):
    ins_n= ioh.insert_network(example_data["network"]) 
    point = example_data["point"]
    ins0 = ioh.insert_point(point)
    point["power"]=60
    ins1 = ioh.insert_point(point)
    point["power"]=61
    ins2 = ioh.insert_point(point)
    point["power"]=62
    ins3 = ioh.insert_point(point)
    sel = ioh.select_point_by_network(ins_n.id)
    assert len(sel)==4
    assert ins0==sel[0]
    assert ins1!=sel[0]
    assert ins1==sel[1]
    assert ins2!=sel[1]
    assert ins2==sel[2]
    assert ins3!=sel[2]
    assert ins3==sel[3]

def test_select_network_by_location(ioh):
    network = deepcopy(example_data["network"])
    del network["id"]
    centlat = example_data["network"]["latitude"]
    centlon = example_data["network"]["longitude"]
    lat = [centlat-10,centlat+10]
    lon = [centlon-10,centlon+10]
    ins= ioh.insert_network(network) 
    network["latitude"]+=4
    network["longitude"]+=4
    ins= ioh.insert_network(network) 
    network["latitude"]+=4
    network["longitude"]-=4
    ins= ioh.insert_network(network) 
    network["latitude"]+=4
    network["longitude"]+=4
    ins= ioh.insert_network(network) 
    network["latitude"]-=4
    network["longitude"]-=4
    ins= ioh.insert_network(network) 
    network["latitude"]-=4
    network["longitude"]+=4
    ins= ioh.insert_network(network) 
    network["latitude"]-=4
    network["longitude"]+=4
    ins= ioh.insert_network(network) 
    network["latitude"]-=4
    network["longitude"]+=4
    ins= ioh.insert_network(network) 
    network["longitude"]+=4
    ins= ioh.insert_network(network) 
    network["longitude"]+=4
    ins= ioh.insert_network(network) 
    network["longitude"]+=4
    ins= ioh.insert_network(network) 
    sel = ioh.select_network_by_location(lat, lon)
    assert len(sel)==6
    for i in sel:
        assert i.latitude <lat[1] and  i.latitude >lat[0]
        assert i.longitude <lon[1] and  i.longitude >lon[0]

def test_select_network_by_location_max_250(ioh):
    network = deepcopy(example_data["network"])
    del network["id"]
    centlat = example_data["network"]["latitude"]
    centlon = example_data["network"]["longitude"]
    lat = [centlat-10,centlat+10]
    lon = [centlon-10,centlon+10]
    for i in range(260):
        ins= ioh.insert_network(network) 
    sel = ioh.select_network_by_location(lat, lon)
    assert len(sel)==250

def test_del_network(ioh):
    ins= ioh.insert_network(example_data["network"]) 
    sel = ioh.select_network(example_data["network"]["id"])
    assert sel is not None
    ioh.delete_network(example_data["network"]["id"])
    sel = ioh.select_network(example_data["network"]["id"])
    assert sel is None

def test_del_network_if_no(ioh):
    sel = ioh.select_network(example_data["network"]["id"])
    assert sel is None
    with pytest.raises(Exception) as excinfo:
        ioh.delete_network(example_data["network"]["id"])
    assert 'no network with id' in excinfo.value.args[0]

def test_del_point(ioh):
    ins1= ioh.insert_network(example_data["network"]) 
    ins = ioh.insert_point(example_data["point"]) 
    id = ins.id
    sel = ioh.select_point(id)
    assert sel is not None
    ioh.delete_point(id)
    sel = ioh.select_point(id)
    assert sel is None

def test_del_point_if_no(ioh):
    sel = ioh.select_point(1)
    assert sel is None
    with pytest.raises(Exception) as excinfo:
        ioh.delete_point(1)
    assert 'no point with id' in excinfo.value.args[0]