# from __future__ import print_statement
import json
import psycopg2
import requests
from requests.cookies import RequestsCookieJar
from flask import Flask
from flask_restful import Resource, Api

from config import *


# post auth to get cookie
r_auth = requests.post(auth_url, data=credential)
resp = json.loads(r_auth.text)
cookie = r_auth.cookies.get('_db_sess')


# get energy data
cookie_jar = RequestsCookieJar()
cookie_jar.set("_db_sess", cookie, domain=".exnaton.com")
get_params = {  'muid' : 'C-2caa1954-b3c8-466c-9722-c1b72dabe32b',
                'start' : '2021-09-01T00:00:00Z',
                'stop' : '2021-10-01T00:00:00Z',
                'measurement' : 'energy',
                'limit' : 5000}
r_get = requests.get(data_url, params=get_params, cookies=cookie_jar)
data_list = json.loads(r_get.text).get('data')


# store data in database
conn = psycopg2.connect(database="postgres", user=db_username, password=db_password, host=db_host, port=db_port)
cursor = conn.cursor()

sql_create_table = """  
    DROP TABLE IF EXISTS energy;
    CREATE TABLE energy (
        id serial4 PRIMARY KEY, 
        measurement varchar(20),
        P0100011D00FF float(8),
        P0100021D00FF float(8),
        time_stamp timestamp
    );"""

sql_insert_data = """
    INSERT INTO energy (measurement, P0100011D00FF, P0100021D00FF, time_stamp) 
    VALUES (%(m)s, %(p1)s, %(p2)s, %(t)s)"""

sql_select = """SELECT * FROM energy;"""


cursor.execute(sql_create_table)
for data in data_list:
    params = {'m' : data.get('measurement'),
              'p1' : data.get('0100011D00FF'),
              'p2' : data.get('0100021D00FF'),
              't' : data.get('timestamp')}
    cursor.execute(sql_insert_data, params)
conn.commit()
conn.close()

# running RESTful API service
app = Flask(__name__)
api = Api(app)

# @app.route('/api/v1/data/energy')
# def hello_world():
#     return '<h1>Hello Totoro!</h1><img src="http://helloflask.com/totoro.gif">'

class EnergyRESTful(Resource):
    def get(self, time_stamp):
        conn = psycopg2.connect(database="postgres", user=db_username, password=db_password, host=db_host, port=db_port)
        cursor = conn.cursor()
        cursor.execute(sql_select)
        fetched_data = cursor.fetchall()
        cursor.close()
        ret = {}
        for data in fetched_data:
            _, _, energy, _, ts = data
            ret[str(ts)] = energy
        return ret

api.add_resource(EnergyRESTful, '/<string:time_stamp>')
app.run(debug=True)

