from sys import stderr
from flask import Flask, request, jsonify, Response
from pymongo import MongoClient, ASCENDING
from os import environ
from datetime import datetime
from flask.helpers import make_response


app = Flask(__name__)
country_id = 0
city_id = 0
temperature_id = 0
countries = []
cities = []
temperatures = []


def get_date(date_str: str):
    date_list = [int(s) for s in date_str.split('-')]
    return datetime(date_list[0], date_list[2], date_list[1])


def startup():
    global countries
    global cities
    global temperatures
    try:
        try:
            client = MongoClient(host=environ['MONGO_HOST'], port=int(environ['MONGO_PORT']), 
                                username=environ['MONGO_USERNAME'], password=environ['MONGO_PASSWORD'])
            db = client['database']
        except Exception as e:
            print(e)
        
        try:
            countries = db.countries
            cities = db.cities
            temperatures = db.temperatures
            print(countries, cities, temperatures)
        except:
            print('countries = mydb.countries')
        
        try: 
            print(db.list_collection_names())
        except Exception as e:
            print(e)

        try: 
            countries.create_index([('id', ASCENDING)], unique=True)
            cities.create_index([('idTara', ASCENDING), ('nume', ASCENDING)], unique=True)
            temperatures.create_index([('idOras', ASCENDING), ('timestamp', ASCENDING)], unique=True)
            print('create_index dones')
        except Exception as e:
            print(e)

    except:
        print('='*50)
        print('someting whent wrong')
        print('='*50)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route('/api/countries', methods=['POST'])
def post_countries():
    params = request.get_json(silent=True)
    if not params:
        return Response(status=400)
    
    if not params.get('nume') or not params.get('lat') or not params.get('lon'):
        return Response(status=409)

    global country_id
    new_country = {'id': country_id, 'nume': params['nume'], 'lat': params['lat'], 'lon': params['lon']}
    try:
        countries.insert_one(new_country);
        country_id += 1;
    except:
        return Response(status=409)

    return make_response(jsonify({'id': country_id - 1}), 201);


@app.route('/api/countries', methods=['GET'])
def get_countries():
    l = [{k: v for k, v in c.items() if k != '_id'} for c in countries.find()]
    return jsonify(l)


@app.route('/api/countries/<country_id>', methods=['PUT'])
def put_countries(country_id):
    params = request.get_json(silent=True)
    if not params:
        return Response(status=400)
        
    if params.get('id', None) is None or not params.get('nume') or not params.get('lat') or not params.get('lon'):
        return Response(status=409)
    
    new_country = {'id': int(country_id), 'nume': params['nume'], 'lat': params['lat'], 'lon': params['lon']}
    try:
        res = temperatures.find_one_and_update({'id': int(country_id)}, {'$set': new_country})
        print(res, file=stderr)
        return Response(status=200 if res else 404)
    except:
        return Response(status=404)


@app.route('/api/countries/<id>', methods=['DELETE'])
def delete_countries(id):
    try:
        res = countries.find_one_and_delete({'id': int(id)})
        return Response(status=200 if res else 404)
    except Exception as e:
        print(e, file=stderr)
        return Response(status=404)


@app.route('/api/cities', methods=['POST'])
def post_city():
    params = request.get_json(silent=True)
    if not params:
        return Response(status=400)
    
    if params.get('idTara', None) is None or not params.get('nume') or not params.get('lat') or not params.get('lon') or \
            not len(list([c for c in countries.find({'id': int(params['idTara'])})])):
        return Response(status=409)
    
    global city_id
    new_city = {'id': city_id, 'idTara': params.get('idTara', 0), 'nume': params['nume'], 'lat': params['lat'], 'lon': params['lon']}
    try:
        cities.insert_one(new_city);
        city_id += 1;
    except Exception as e:
        print(e, file=stderr)
        return Response(status=409)

    return make_response(jsonify({'id': city_id - 1}), 201);


@app.route('/api/cities', methods=['GET'])
def get_cities():
    l = [{k: v for k, v in c.items() if k != '_id'} for c in cities.find()]
    return jsonify(l)


@app.route('/api/cities/country/<id_country>', methods=['GET'])
def get_cities_by_country(id_country):
    l = [{k: v for k, v in c.items() if k != '_id'} for c in cities.find({'idTara': int(id_country)})]
    print(*l, '\n', sep='\n', file=stderr)
    return jsonify(l)


@app.route('/api/cities/<id_city>', methods=['PUT'])
def put_cities(id_city):
    params = request.get_json(silent=True)
    if not params:
        return Response(status=400)
    if params.get('id', None) is None or params.get('idTara', None) is None or not params.get('nume') or not params.get('lat') or not params.get('lon'):
        return Response(status=409)
    
    new_city = {'id': int(id_city), 'idTara': params.get('idTara', 0), 'nume': params['nume'], 'lat': params['lat'], 'lon': params['lon']}
    try:
        res = temperatures.find_one_and_update({'id': int(id_city)}, {'$set': new_city})
        print(res, file=stderr)
        return Response(status=200 if res else 404)
    except Exception as e:
        print(e, file=stderr)
        return Response(status=404)


@app.route('/api/cities/<id_city>', methods=['DELETE'])
def delete_cities(id_city):
    try:
        res = cities.find_one_and_delete({'id': int(id_city)})
        return Response(status=200 if res else 404)
    except Exception as e:
        print(e, file=stderr)
        return Response(status=404)


@app.route('/api/temperatures', methods=['POST'])
def post_temperatures():
    params = request.get_json(silent=True)
    if not params:
        return Response(status=400);
    
    if params.get('idOras', None) is None or params.get('valoare', None) is None or \
            not len(list([c for c in cities.find({'id': int(params['idOras'])})])) or not isinstance(params['valoare'], float):
        return Response(status=409)
    
    global temperature_id
    new_temperature = {'id': temperature_id, 'idOras': params['idOras'], 'valoare': params['valoare'], 'timestamp': datetime.utcnow()}
    try:
        temperatures.insert_one(new_temperature);
        temperature_id += 1;
    except Exception as e:
        print(e, file=stderr)
        return Response(status=409)
    
    return make_response(jsonify({'id': temperature_id - 1}), 201)


@app.route('/api/temperatures', methods=['GET'])
def get_temperatures():
    params = request.args

    query = {}
    if params and params.get('lat', None) is not None:
        query['lat'] = float(params['lat'])
    if params and params.get('lon', None) is not None:
        query['lon'] = float(params['lon'])

    cities_ids = []
    for city in cities.find(query):
            cities_ids.append(int(city['id']))

    required_temperatures = []
    for temp in temperatures.find():
        if temp['idOras'] not in cities_ids:
            continue
        if params and params.get('until', None) is not None:
            if get_date(params['until']) < temp['timestamp']:
                continue
        if params and params.get('from', None) is not None:
            if get_date(params['from']) > temp['timestamp']:
                continue
        
        required_temperatures.append(temp)
    
    l = [{k: v for k, v in c.items() if k != '_id' and k != 'idOras'} for c in required_temperatures]
    return jsonify(l)


@app.route('/api/temperatures/cities/<id_city>', methods=['GET'])
def get_temperatures_by_city(id_city):
    params = request.args
    required_temperatures = []
    for temp in temperatures.find({'idOras': int(id_city)}):
        if params and params.get('until', None) is not None:
            if get_date(params['until']) < temp['timestamp']:
                continue
        if params and params.get('from', None) is not None:
            if get_date(params['from']) > temp['timestamp']:
                continue
        
        required_temperatures.append(temp)
    
    l = [{k: v for k, v in c.items() if k != '_id' and k != 'idOras'} for c in required_temperatures]
    return jsonify(l)


@app.route('/api/temperatures/countries/<id_country>', methods=['GET'])
def get_temperatures_by_country(id_country):
    params = request.args

    cities_ids = []
    for city in cities.find({'idTara': int(id_country)}):
            cities_ids.append(int(city['id']))

    required_temperatures = []
    for temp in temperatures.find():
        if temp['idOras'] not in cities_ids:
            continue
        if params and params.get('until', None) is not None:
            if get_date(params['until']) < temp['timestamp']:
                continue
        if params and params.get('from', None) is not None:
            if get_date(params['from']) > temp['timestamp']:
                continue
        
        required_temperatures.append(temp)
    
    l = [{k: v for k, v in c.items() if k != '_id' and k != 'idOras'} for c in required_temperatures]
    return jsonify(l)


@app.route('/api/temperatures/<id_temperature>', methods=['PUT'])
def put_temperatures(id_temperature):
    params = request.get_json(silent=True)
    if not params:
        return Response(status=400)

    if params.get('id', None) is None or params.get('idOras', None) is None or params.get('valoare', None) is None:
        return Response(status=409)
    
    new_temperature = {'id': int(id_temperature), 'idOras': params['idOras'], 'valoare': params['valoare'], 'timestamp': datetime.utcnow()}
    try:
        res = temperatures.find_one_and_update({'id': int(id_temperature)}, {'$set': new_temperature})
        print(res, file=stderr)
        return Response(status=200 if res else 404)
    except Exception as e:
        print(e, file=stderr)
        return Response(status=404)


@app.route('/api/temperatures/<id_temperature>', methods=['DELETE'])
def delete_temperatures(id_temperature):
    try:
        res = temperatures.find_one_and_delete({'id' : int(id_temperature)})
        return Response(status=200 if res else 404)
    except Exception as e:
        print(e)
        return Response(status=404)


def main():
    startup()
    app.run(host=environ['FLASK_HOST'], port=int(environ['FLASK_PORT']), debug=True)


if __name__ == '__main__':
    main()
