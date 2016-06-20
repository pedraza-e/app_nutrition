from flask import request, render_template
from flaskexample import app
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import pandas as pd
import psycopg2
from my_Model1 import ModelIt

user = 'username' #add your username here (same as previous postgreSQL)                      
host = 'localhost'
dbname = 'food_db'
pswd='yourpassword'
db = create_engine('postgres://%s%s/%s'%(user,host,dbname))
con = None
con = psycopg2.connect(database = dbname, user = user, host=host, password=pswd)

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html",
       title = 'Home', user = { 'nickname': 'Miguel' },
       )

@app.route('/db')
def birth_page():
    sql_query = """                                                                       
                SELECT pos AS "food", AVG(energy) AS "energy", AVG(carbs) AS "carbs", AVG(protein) AS "protein", AVG(iron) AS "iron", AVG(vit_a) AS "vit_a", AVG(vit_c) AS "vit_c", AVG(price_serv) AS "price" FROM nutrients_table GROUP BY pos ORDER BY pos;
        
                """
    query_results = pd.read_sql_query(sql_query,con)
    births = ""
    for i in range(0,8):
        births += query_results.iloc[i]['food']
        births += "<br>"
    return births

@app.route('/db_fancy')
def cesareans_page_fancy():
    sql_query = """
               SELECT pos AS "food", AVG(energy) AS "energy", AVG(price_serv) AS "price" FROM nutrients_table GROUP BY pos ORDER BY pos;
                """
    query_results=pd.read_sql_query(sql_query,con)
    births = []
    for i in range(0,query_results.shape[0]):
        births.append(dict(index=query_results.iloc[i]['food'], attendant=query_results.iloc[i]['energy'], birth_month=query_results.iloc[i]['price']))
    return render_template('cesareans.html',births=births)

@app.route('/input')
def cesareans_input():
    return render_template("input.html")

@app.route('/output')
def cesareans_output():
  #pull 'birth_month' from input field and store it
  patient = request.args.get('birth_month')
  ucase = request.args.get('ucase')
  #pull 'bad_foods' from input field and store it
  bad_foods = request.args.get('bad_foods')
  ucase = request.args.get('ucase')
  #just select the Cesareans  from the birth database for the month that the user inputs
  query = """SELECT * FROM nutrients_table2;"""
  #print query
  query_results=pd.read_sql_query(query,con)

  query2 = """SELECT * FROM dri_table;"""
  #print query
  query_results2=pd.read_sql_query(query2,con)

  #print query_results
  births = []
  for i in range(0,query_results.shape[0]):
      births.append(dict(pos=query_results.iloc[i]['pos'], energy=query_results.iloc[i]['energy'], price_serv=query_results.iloc[i]['price_serv']))
      
  the_result = []
  the_result, result_nutrients, nutrients4, total_cost = ModelIt(query_results, ucase, query_results2, patient, bad_foods)
  #the_result = len(the_result)
  return render_template("output.html", births = births, the_result = the_result, result_nutrients=result_nutrients, nutrients4=nutrients4, total_cost=total_cost, ucase=ucase, sites=query_results.to_html())

