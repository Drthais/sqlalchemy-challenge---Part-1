# Import the dependencies.
import pandas as pd
from flask import Flask, jsonify

from sqlalchemy import create_engine, inspect, text, desc
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
Base.prepare(autoload_with=engine)

# reflect the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Save references to each table


# Create our session (link) from Python to the DB
session = Session(engine)
conn = engine.connect() 

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )
    
@app.route("/api/v1.0/precipitation")
def prcp():
    query = text("""SELECT date, prcp
    FROM Measurement
    WHERE date >= (SELECT DATE(MAX(date), '-1 year') FROM Measurement)
    ORDER BY date;""")
    df = pd.read_sql(query, con=conn)
    data = df.values.tolist()
    result = {}
    for i in data:
        result[i[0]]= i[1]
    return result
    
    
@app.route("/api/v1.0/station")
def station():   
    query = text("""SELECT station from station""")
    df = pd.read_sql(query, con=conn)
    data = df.values.tolist()
    result = []
    for i in data:
        result.append(i[0])
    return result
    
@app.route("/api/v1.0/tobs")
def tobs():
    query = text("""
            SELECT date, tobs
            FROM Measurement
            WHERE station = (SELECT station 
                            FROM Measurement
                            GROUP BY station
                            ORDER BY COUNT(*) DESC
                            LIMIT 1)
            AND date >= (SELECT DATE(MAX(date), '-1 year') FROM Measurement);
        """)
    df = pd.read_sql(query, con=conn)
    return df.values.tolist()

    
@app.route("/api/v1.0/<start>/<end>") 
def temp_obs2(start, end): 
    
    query = text(
        """ 
        SELECT 
            MIN(tobs) AS min_temp, 
            AVG(tobs) AS avg_temp,
            MAX(tobs) AS max_temp
        FROM Measurement
        WHERE date >= :start AND date <= :end; 
        """
    )
    params = {'start': start, 'end': end} 
    

    df = pd.read_sql(query, con=conn, params=params) 
    return df.values.tolist()[0]

@app.route("/api/v1.0/<start>") 
def temp_obs(start): 
    query = text(
        """ 
        SELECT 
            MIN(tobs) AS min_temp, 
            AVG(tobs) AS avg_temp,
            MAX(tobs) AS max_temp
        FROM Measurement
        WHERE date >= :start; 
        """
    )
    params = {'start': start}

    df = pd.read_sql(query, con=conn, params=params) 
    return df.values.tolist()[0] 
    
 
    
if __name__ == '__main__':
    app.run(debug=True)