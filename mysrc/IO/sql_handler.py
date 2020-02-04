from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, not_
# looks ugly but allows to avoid errors with sys.path when running module as main or from different source
if __name__ == "__main__": 
    from my_tables import ChargeNetwork, ChargePoint, Base, create_
else:
    from .my_tables import ChargeNetwork, ChargePoint, Base, create_

cmapError = "cmapError: "

class iohandler():

    def __init__(self,session):
        self.session = session
    
    def check_all_needed(self, net_keys, needed_list):
        missing = list(filter(lambda key: key not in net_keys, needed_list))
        if len(missing)>0:
            raise Exception(f"{cmapError}missing values of a {','.join(missing)}")
            
    def insert_network(self, network):
        self.check_all_needed(network.keys(), ChargeNetwork.needed_list)
        ins = ChargeNetwork(
            latitude=network["latitude"],
            longitude=network["longitude"],
            unit_cost=network["unit_cost"],
            owner=network["owner"]
        )
        if "id" in network.keys():
            ins.id = network["id"]
        try:
            self.session.add(ins) 
            self.session.commit()
        except Exception as e:
            if "psycopg2.errors.UniqueViolation" in e.args[0]:
                raise Exception(f"{cmapError}id = {network['id']} already exists")
        return ins

    def insert_point(self, point):
        self.check_all_needed(point.keys(), ChargePoint.needed_list)

        ins = ChargePoint(
            power=float(point["power"]),
            id_charge_network=point["id_charge_network"]
        )

        if "id" in point.keys():
            ins.id = point["id"]
        try:
            self.session.add(ins) 
            net = self.select_network(point["id_charge_network"])
            sel = self.select_point_by_network(point["id_charge_network"])
            powl = [i.power for i in sel]
            net.avg_power = sum(powl)/len(powl)
            self.session.commit()
        except Exception as e:
            if "psycopg2.errors.UniqueViolation" in e.args[0]:
                raise Exception(f"{cmapError}id = {point['id']} already exists")
            elif "(psycopg2.errors.ForeignKeyViolation)"  in e.args[0]:
                raise Exception(f"{cmapError} No parent Network at id :{point['id_charge_network']}")


        return ins

    def select_network(self,id):
        return self.session.query(ChargeNetwork).filter(
            ChargeNetwork.id == id
        ).first()

    def select_network_all(self):
        return self.session.query(ChargeNetwork).all()

    def select_network_by_location(self, lat, lon):
        return self.session.query(ChargeNetwork).filter(
            and_(
                ChargeNetwork.latitude.between(lat[0],lat[1]),
                ChargeNetwork.longitude.between(lon[0],lon[1])
            )
        ).limit(250).all()

    def select_point(self,id):
        return self.session.query(ChargePoint).filter(
            ChargePoint.id == id
        ).first()

    def select_point_all(self):
        return self.session.query(ChargePoint).all()

    def select_point_by_network(self,network_id):
        return self.session.query(ChargePoint).filter(
            ChargePoint.id_charge_network == network_id
        ).all()

    def update_network(self, network):
        sel = self.select_network(network["id"])
        if sel is None:
            raise Exception(f"{cmapError}no network with id {network['id']}")
        for i in network.keys():
            if i =="latitude": sel.latitude=network["latitude"]
            elif i =="longitude": sel.longitude=network["longitude"]
            elif i =="unit_cost": sel.unit_cost=network["unit_cost"]
            elif i =="owner": sel.owner=network["owner"]
        self.session.commit()
        return sel

    def update_point(self, point):
        sel1 = self.select_point(point["id"])
        if sel1 is None:
            raise Exception(f"{cmapError}no point with id {point['id']}")
        for i in point.keys():
            if i =="power": sel1.power=float(point["power"])
            elif i =="id_charge_network": sel1.id_charge_network=point["id_charge_network"]
        
        net = self.select_network(sel1.id_charge_network)
        sel = self.select_point_by_network(sel1.id_charge_network)
        powl = [i.power for i in sel]
        net.avg_power = sum(powl)/len(powl)
        self.session.commit()
        return sel1

    def delete_network(self, network_id):
        sel = self.select_network(network_id)
        if sel is None:
            raise Exception(f"{cmapError}no network with id {network_id}")
        self.session.delete(sel)
        self.session.commit()

    def delete_point(self, point_id):
        sel = self.select_point(point_id)
        if sel is None:
            raise Exception(f"{cmapError}no point with id {point_id}")
        self.session.delete(sel)
        net = self.select_network(sel.id_charge_network)
        sel = self.select_point_by_network(net.id)
        powl = [i.power for i in sel]
        if len(powl)>0:
            net.avg_power = sum(powl)/len(powl)
        else:
            net.avg_power = 0
        self.session.commit()

        
if __name__ == "__main__":
    from file_reader import myhost
    host = myhost("mysrc/config.json")
    engine = create_engine(host)
    session = Session(engine)
    ioh = iohandler(session)
    network={
        "id":1,
        "latitude":30,
        "longitude":30,
        "unit_cost":55.345,
        "owner":"Meh",
        "avg_power":"80.567573552"
    }
    point={
        "power":50,
        "id_charge_network":1
    }
    ioh.insert_network(network)
    ioh.insert_point(point)
    pass