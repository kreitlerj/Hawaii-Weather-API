# Import dependencies
import numpy as np

import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references for each table
Measurement = Base.classes.measurement
Station = Base.classes.station


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
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
        f"<br/>"
        f"start/end should be in date format: yyyy-mm-dd<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipiation():
    """Return a list of the last 12 months of precipiation data by date"""

    # Create our session from Python to the DB
    session = Session(engine)

    #Calculate the date 12 months prior to the last date of data recorded (2017-08-23)
    query_date = dt.date(2017, 8, 23)- dt.timedelta(days=365)

    # Query the last 12 months of precipiation data
    results = session.query(Measurement.date, func.max(Measurement.prcp)).\
                        filter(Measurement.date >= query_date).group_by(Measurement.date).all()

    # Create a dictionary from the row data and append to a list 12 months of precipiation data
    prcp_data = []
    for day in results:
        prcp_dict = {}
        prcp_dict[day[0]] = day[1]
        prcp_data.append(prcp_dict)

    return jsonify(prcp_data)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of all stations"""
    # Create our session from Python to the DB
    session = Session(engine)

    # Query all passengers
    results = session.query(Station.name).all()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of 12 months of observed temperatures"""
    # Create our session from Python to the DB
    session = Session(engine)

    #Calculate the date 12 months prior to the last date of data recorded (2017-08-23)
    query_date = dt.date(2017, 8, 23)- dt.timedelta(days=365)
    
    # Query tobs based on the max temp recorded for the past 12 months
    results = session.query(Measurement.date, func.max(Measurement.tobs)).\
                filter(Measurement.date >= query_date).group_by(Measurement.date).all()


    # Create a dictionary of row data with the date as the key and the tobs as the value
    tobs_data = []
    for day in results:
        tobs_dict = {}
        tobs_dict[day[0]] = day[1]
        tobs_data.append(tobs_dict)

    return jsonify(tobs_data)

@app.route("/api/v1.0/<start>")
def start(start):
    """Return a list of TMIN, TAVG, TMAX for a given start date"""
    # Create our session from Python to the DB
    session = Session(engine)

    # Query temperature data for date greater than or equal to the start date
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).all() 

    # Convert list containing a tuple into a list containing a dictionary
    temp_data = [{'TMIN': results[0][0], 'TAVG': results[0][1], 'TMAX': results[0][2]}]

    return jsonify(temp_data)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    """Return a list of TMIN, TAVG, TMAX for a given start date"""
    # Create our session from Python to the DB
    session = Session(engine)

    # This function called `calc_temps` will accept start date and end date in the format '%Y-%m-%d' 
    # and return the minimum, average, and maximum temperatures for that range of dates
    def calc_temps(start_date, end_date):
        """TMIN, TAVG, and TMAX for a list of dates.
        
        Args:
            start_date (string): A date string in the format %Y-%m-%d
            end_date (string): A date string in the format %Y-%m-%d
            
        Returns:
            TMIN, TAVE, and TMAX
        """
        
        return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all() 
     
    results = calc_temps(start, end)

    # Collect the function returned data into a list containing a dictionary
    temp_data = [{'TMIN': results[0][0], 'TAVG': results[0][1], 'TMAX': results[0][2]}]

    return jsonify(temp_data)
if __name__ == '__main__':
    app.run(debug=True)
