from flask import Flask
print(__name__)
from IO.my_tables import create_, ChargeNetwork, ChargePoint
from IO.sql_handler import iohandler, cmapError
from IO.file_reader import myhost
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

app = Flask(__name__)
from flask import request, jsonify

mho = myhost("config.json")
engine = create_engine(mho)
create_(engine)
session = Session(engine)
ioh = iohandler(session)

default_response="something went wrong"


def Home_decorator(func):
    def wrapper():
        res = default_response
        try:
            func()
            response = ioh.select_network_all()
            res = showall(response)
        except Exception as e:
            if cmapError in e.args[0]:
                res=e.args[0]
        finally:
            return jsonify(res)
    wrapper.__name__ = func.__name__
    return wrapper

def format_network(network):
    dic = network_to_json(network)
    points = ioh.select_point_by_network(network.id)
    for point in points:
        dic["points"].append({
            "id":point.id,
            "power":float(point.power)
        })
    return dic


def showall(mylist):
    res = []
    if len(mylist)==0:
        return "nothing to show"
    for i in mylist:
        dic = format_network(i)
        res.append(dic)
    return res

def network_to_json(network):
    return {
        "id":network.id,
        "avg_power":float(network.avg_power),
        "localisation":{
            "lat":network.latitude,
            "lon":network.longitude
        },
        "unit_cost":float(network.unit_cost),
        "owner":network.owner,
        "timestamp":{
            "created_on":network.created_on,
            "updated_on":network.updated_on,
        },"points":[]
    }

@app.route("/", methods=["GET"])
def home():
    response = ''
    if "id" in request.args:
        response = [ioh.select_network(int(request.args["id"]))]
    elif "lon"in request.args and "lat"in request.args:
        lon = [float(i) for i in request.args["lon"].split(",")]
        lat = [float(i) for i in request.args["lat"].split(",")]
        response = ioh.select_network_by_location(lat,lon)
    else:
        response = ioh.select_network_all()
    res = showall(response)
    return jsonify(res)


@app.route("/", methods=["POST","PUT"])
@Home_decorator
def home_add():
    if request.method == 'POST':
        ioh.insert_network(dict(request.args))
    elif request.method == 'PUT':
        ioh.insert_point(dict(request.args))


@app.route("/", methods=["PATCH"])
@Home_decorator
def home_update():
    if request.args["type"] == 'network':
        ioh.update_network(dict(request.args))
    elif request.args["type"] == 'point':
        ioh.update_point(dict(request.args))

@app.route("/", methods=["DELETE"])
@Home_decorator
def home_delete():
    if "id" not in request.args:
        raise Exception(f"missing value of id ")
    if request.args["type"] == 'network':
        ioh.delete_network(request.args["id"])
    elif request.args["type"] == 'point':
        ioh.delete_point(request.args["id"])

@app.route("/<int:my_id>", methods=["GET","PUT","POST","DELETE","PATCH"])
def get_by_network(my_id):
    response = default_response
    try:
        if request.method == 'POST' or request.method == 'PUT':
            mydict = dict(request.args)
            mydict["id_charge_network"]=my_id
            ioh.insert_point(mydict)
        if request.method == 'DELETE':
            if "id" not in request.args:
                raise Exception(f"missing value of id ")
            id = request.args["id"]
            ioh.delete_point(id)
        if request.method == 'PATCH':
            if "id" not in request.args:
                raise Exception(f"missing value of id ")
            mydict = dict(request.args)
            mydict["id_charge_network"]=my_id
            ioh.update_point(mydict)
        network = ioh.select_network(my_id)
        response = format_network(network)
    except Exception as e:
        if cmapError in e.args[0]:
            response=e.args[0]
    finally:
        return jsonify(response)




if __name__=="__main__":
    app.run(debug=True)