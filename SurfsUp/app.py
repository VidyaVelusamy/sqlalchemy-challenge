# Import the dependencies.
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
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Stations = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

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
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def Precipitation():
    

    recentdate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    # Calculate the date one year from the last date in data set.
    Year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)


    # Perform a query to retrieve the data and precipitation scores
    precip_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= Year_ago).\
        order_by(Measurement.date).all()

   

    
    # Create a dictionary from the row data and append to a list of all_passengers
    all_data = []
    for date,prcp in precip_data:
        precipitation_dict = {}
        precipitation_dict["Date"] = date
        precipitation_dict["Precipitation"] = prcp
        
        all_data.append(precipitation_dict)
    session.close()

    return jsonify(all_data)

@app.route("/api/v1.0/stations")
def names():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all station names"""
    # Query all passengers
    results = session.query(Measurement.station).all()

    session.close()

    # Convert list of tuples into normal list
    all_names = list(np.ravel(results))

    return jsonify(all_names)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    recentdate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    most_active_station = session.query(Measurement.station,func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()
    most_active_station_id = most_active_station.station
    # Calculate the date one year from the last date in data set.
    Year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    """Return a list of all station names"""
    # Query all passengers
    temperature_data = (session.query(Measurement.date,Measurement.tobs)
                    .filter(Measurement.station == most_active_station_id)
                    .filter(Measurement.date >= Year_ago)
                    .all())
    # Extract temperature values
    dates = [date[0] for date in temperature_data]
    
    temperatures = [temp[1] for temp in temperature_data]
    session.close()

    # Combine dates and temperatures into a list of dictionaries
    result = [{'date': date, 'temperature': temperature} for date, temperature in zip(dates, temperatures)]


    return jsonify(result)
@app.route("/api/v1.0/<start>")
def temperature_stats_start(start):
    session = Session(engine)
    
    # Convert start date from string to datetime object
    start_date = dt.datetime.strptime(start, '%Y-%m-%d').date()
    
    # Query to get TMIN, TAVG, TMAX for dates greater than or equal to start date
    results = session.query(func.min(Measurement.tobs).label('TMIN'),
                            func.avg(Measurement.tobs).label('TAVG'),
                            func.max(Measurement.tobs).label('TMAX')) \
                    .filter(Measurement.date >= start_date) \
                    .all()
    
    session.close()

    # Extract results into a dictionary
    temperatures = []
    for result in results:
        temp_dict = {}
        temp_dict['TMIN'] = result.TMIN
        temp_dict['TAVG'] = result.TAVG
        temp_dict['TMAX'] = result.TMAX
        temperatures.append(temp_dict)
    
    return jsonify(temperatures)

@app.route("/api/v1.0/<start>/<end>")
def temperature_stats_start_end(start, end):
    session = Session(engine)
    
    # Convert start and end dates from strings to datetime objects
    start_date = dt.datetime.strptime(start, '%Y-%m-%d').date()
    end_date = dt.datetime.strptime(end, '%Y-%m-%d').date()
    
    # Query to get TMIN, TAVG, TMAX for dates between start and end dates (inclusive)
    results = session.query(func.min(Measurement.tobs).label('TMIN'),
                            func.avg(Measurement.tobs).label('TAVG'),
                            func.max(Measurement.tobs).label('TMAX')) \
                    .filter(Measurement.date >= start_date) \
                    .filter(Measurement.date <= end_date) \
                    .all()
    
    session.close()

    # Extract results into a dictionary
    temperatures = []
    for result in results:
        temp_dict = {}
        temp_dict['TMIN'] = result.TMIN
        temp_dict['TAVG'] = result.TAVG
        temp_dict['TMAX'] = result.TMAX
        temperatures.append(temp_dict)
    
    return jsonify(temperatures)
if __name__ == '__main__':
    app.run(debug=True)