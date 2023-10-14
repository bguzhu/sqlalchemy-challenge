# Import the necessary dependencies
import datetime as dt
import numpy as np
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
#################################################
# Database Setup
#################################################
# create engine to hawaii.sqlite, which allows to connect to the sqlite database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

#creates a base to see the content of the sqlite
Base = automap_base()

# Use Base to reflect the tables into classes
Base.prepare(engine)

#Assign the measurement and station classes to variables of the same name
Measurement = Base.classes.measurement
Station = Base.classes.station

#Creating a sqlalchemy session in order to link Python to the database
session = Session(engine)

#################################################
# Flask Setup
#################################################
#Create the app through Flask
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
#Make the routes and define the classes with names of your choice
@app.route("/")
def welcome():
    #Show the available routes in the main homepage with an added note for how to use the last two routes(also, last f string is on a different line with <p>)
    return (
        f"Welcome to the Hawaii Climate Analysis Homepage<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
        f"<p>start and end should be replaced as MMDDYYYY.</p>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    previous_year = dt.date(2017,8,23) - dt.timedelta(days=365)

    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= previous_year).all()
    
    #Close the session once the data is gathered
    session.close()
    precip = { date: prcp for date, prcp in precipitation}

    return jsonify(precip)

@app.route("/api/v1.0/stations")
def stations():
    stations = session.query(Station.station).all()

    session.close()

    #Converts list of tuples(ordered, finite list of elements) into a normal list
    stations = list(np.ravel(stations))

    #Shows the list of stations from line 68 with stations as the list name(left side of equal sign in jsonify statement)
    return jsonify(stations = stations)

@app.route("/api/v1.0/tobs")
def tobs():
    previous_year = dt.date(2017,8,23) - dt.timedelta(days=365)

    tobs = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= previous_year).all()

    session.close()

    tobs = list(np.ravel(tobs))

    return jsonify(tobs=tobs)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def stats(start=None, end=None):

    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    #Conditional for when there is no end date
    if not end:
        start = dt.datetime.strptime(start, "%m%d%Y")
        stats = session.query(*sel).\
            filter(Measurement.date >= start).all()
        
        session.close()

        stats = list(np.ravel(stats))

        return jsonify(temps = stats)
    
    start = dt.datetime.strptime(start, "%m%d%Y")
    end = dt.datetime.strptime(end, "%m%d%Y")

    stats = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    
    session.close()

    stats = list(np.ravel(stats))

    return jsonify(temps = stats)

if __name__ == '__main__':
    app.run(debug=True)