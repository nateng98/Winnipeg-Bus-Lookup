"""
Connects to a SQL database using pymssql
"""
import configparser
from flask import Flask, render_template, request

# import pyodbc as odbc to run on local windows machine
# import pyodbc as odbc

import pymssql as mssql

# import socket to get hostname of aviary
import socket

app = Flask(__name__)

def read_config(file_path):
  config = configparser.ConfigParser()
  config.read(file_path)
  return config

config_file = 'config.ini'
config = read_config(config_file)

# # LOCALHOST - Access values from the configuration file (config.ini)
# driver_name = config.get('Database', 'Driver')
# server_name = config.get('Database', 'Server')
# database_name = config.get('Database', 'Database')
# encrypt = config.get('Database', 'Encrypt')
# trusted_connection = config.get('Database', 'Trusted_Connection')

# # This is the connection string for pyodbc
# connection_string = (
#   f'DRIVER={{{driver_name}}};'
#   f'SERVER={server_name};'
#   f'DATABASE={database_name};'
#   f'Encrypt={encrypt};'
#   f'Trusted_Connection={trusted_connection};'
# )
# conn = odbc.connect(connection_string)


# URANIUM - Access values from the configuration file (config.ini)
server_name = config.get('Database', 'Server')
user = config.get('Database', 'User')
password = config.get('Database', 'Password')
database_name = config.get('Database', 'Database')

conn = mssql.connect(
  server=server_name,
  user=user,
  password=password,
  database=database_name
)

cursor = conn.cursor()

@app.route('/')
def home():
  return render_template('index.html')

@app.route('/display')
def display_table():
  return render_template('display.html')

#   return render_template('display_table.html', table_rows=table_rows)

# ====================================================================================================
# ====================================================================================================
@app.route('/query1', methods=['POST'])
def query1():
  cursor = conn.cursor()
  cursor.execute('''
    SELECT BusRoute.route_number, BusRoute.route_name, BusStop.stop_number, BusStop.longitude, BusStop.latitude
    FROM BusRoute
    JOIN Contain ON BusRoute.route_number = Contain.route_number
    JOIN BusStop ON Contain.stop_number = BusStop.stop_number;
  ''')
  result = cursor.fetchall()
    
  # Get the column names from cursor description
  columns = [column[0] for column in cursor.description]
    
  return render_template('display.html', columns=columns, result=result)
# ====================================================================================================
# ====================================================================================================
@app.route('/query2', methods=['POST'])
def query2():
  route_num = request.form['route_num']
  the_date = request.form['the_date']
  cursor = conn.cursor()
  cursor.execute(f'''
    WITH RouteHourDeviation AS (
      SELECT Arrival.route_number, Arrival.the_date, TheHour.the_time, SUM(Arrival.deviation) AS total_deviation
      FROM Arrival
      JOIN TheHour ON Arrival.the_time = TheHour.the_time
      WHERE Arrival.route_number = '{route_num}' AND Arrival.the_date = '{the_date}'
      GROUP BY Arrival.route_number, Arrival.the_date, TheHour.the_time
    )
    SELECT DISTINCT route_number, the_date, the_time, total_deviation
    FROM RouteHourDeviation
    WHERE total_deviation = (SELECT MAX(total_deviation) FROM RouteHourDeviation);
  ''')
  result = cursor.fetchall()
    
  # Get the column names from cursor description
  columns = [column[0] for column in cursor.description]
    
  return render_template('display.html', columns=columns, result=result)
# ====================================================================================================
# ====================================================================================================
@app.route('/query3', methods=['POST'])
def query3():
  top_num = request.form['top_num']
  cursor = conn.cursor()
  cursor.execute(f'''
    WITH TotalTrafficDays AS (
      SELECT top {top_num} Weather.the_date, SUM(Traffic.total) as sum_traffic
      FROM Weather
      JOIN Traffic ON Weather.the_date = Traffic.the_date
      GROUP BY Weather.the_date
      ORDER BY SUM(Traffic.total) DESC
    )
    SELECT Weather.the_date, Weather.max_temp, Weather.min_temp, Weather.total_precip_mm, Weather.snow_on_grnd_cm, TotalTrafficDays.sum_traffic
    FROM Weather
    JOIN TotalTrafficDays ON Weather.the_date = TotalTrafficDays.the_date;
  ''')
  result = cursor.fetchall()
    
  # Get the column names from cursor description
  columns = [column[0] for column in cursor.description]
    
  return render_template('display.html', columns=columns, result=result)
# ====================================================================================================
# ====================================================================================================
@app.route('/query4', methods=['POST'])
def query4():
  traffic = request.form['traffic']
  cursor = conn.cursor()
  cursor.execute(f'''
    WITH HighTrafficDays AS (
    SELECT DISTINCT PassUp.the_date
    FROM PassUp
    JOIN Traffic ON PassUp.the_date = Traffic.the_date
    WHERE Traffic.total > {traffic}
  )
  SELECT PassUp.route_number, PassUp.route_destination, PassUp.the_date, PassUp.the_time
  FROM PassUp
  JOIN HighTrafficDays ON PassUp.the_date = HighTrafficDays.the_date;
  ''')
  result = cursor.fetchall()
    
  # Get the column names from cursor description
  columns = [column[0] for column in cursor.description]
    
  return render_template('display.html', columns=columns, result=result)
# ====================================================================================================
# ====================================================================================================
@app.route('/query5', methods=['POST'])
def query5():
  cursor = conn.cursor()
  cursor.execute(f'''
    WITH HighDeviationDays AS (
      SELECT the_date, AVG(deviation) AS avg_deviation
      FROM Arrival
      GROUP BY the_date
      HAVING AVG(deviation) > 30
    )
    SELECT HighDeviationDays.the_date, HighDeviationDays.avg_deviation, RouteBranch.route_number, RouteBranch.route_destination
    FROM HighDeviationDays
    JOIN Arrival ON HighDeviationDays.the_date = Arrival.the_date
    JOIN RouteBranch ON Arrival.route_number = RouteBranch.route_number AND Arrival.route_destination = RouteBranch.route_destination;
  ''')
  result = cursor.fetchall()
    
  # Get the column names from cursor description
  columns = [column[0] for column in cursor.description]
    
  return render_template('display.html', columns=columns, result=result)
# ====================================================================================================
# ====================================================================================================
@app.route('/query6', methods=['POST'])
def query6():
  top_num = request.form['top_num']
  cursor = conn.cursor()
  cursor.execute(f'''
    WITH BoardingAlightingDifference AS (
      SELECT top {top_num} stop_number, ABS(SUM(average_boardings) - SUM(average_alightings)) AS boarding_alighting_difference
      FROM PassengerMass
      GROUP BY stop_number
    )
    SELECT BusStop.stop_number, BusStop.longitude, BusStop.latitude, boarding_alighting_difference
    FROM BusStop
    JOIN BoardingAlightingDifference ON BusStop.stop_number = BoardingAlightingDifference.stop_number
    ORDER BY boarding_alighting_difference DESC;
  ''')
  result = cursor.fetchall()
    
  # Get the column names from cursor description
  columns = [column[0] for column in cursor.description]
    
  return render_template('display.html', columns=columns, result=result)
# ====================================================================================================
# ====================================================================================================
@app.route('/query7', methods=['POST'])
def query7():
  the_date = request.form['the_date']
  cursor = conn.cursor()
  cursor.execute(f'''
    Select avg(deviation) as Average_Deviation from Arrival where the_date < '{the_date}'
    UNION
    Select avg(deviation) as Average_Deviation from Arrival where the_date >= '{the_date}'
  ''')
  result = cursor.fetchall()
    
  # Get the column names from cursor description
  columns = [column[0] for column in cursor.description]
    
  return render_template('display.html', columns=columns, result=result)
# ====================================================================================================
# ====================================================================================================
@app.route('/query8', methods=['POST'])
def query8():
  cursor = conn.cursor()
  cursor.execute('''
    WITH WeatherConditionDeviations AS (
      SELECT Arrival.route_number, Weather.precip_type, AVG(Arrival.deviation) AS avg_deviation
      FROM Arrival
      JOIN Weather ON Arrival.the_date = Weather.the_date
      GROUP BY Arrival.route_number, Weather.precip_type
    )
    SELECT route_number, precip_type, avg_deviation
    FROM WeatherConditionDeviations;
  ''')
  result = cursor.fetchall()
    
  # Get the column names from cursor description
  columns = [column[0] for column in cursor.description]
    
  return render_template('display.html', columns=columns, result=result)
# ====================================================================================================
# ====================================================================================================
@app.route('/query9', methods=['POST'])
def query9():
  cursor = conn.cursor()
  cursor.execute('''
    WITH RankedStops AS (
      SELECT Traffic.the_date, Traffic.the_time, BusStop.stop_number, BusStop.longitude, BusStop.latitude,
          RANK() OVER (PARTITION BY Traffic.the_date, Traffic.the_time ORDER BY Traffic.total DESC) AS traffic_rank
      FROM Traffic
      JOIN BusStop ON cast(Traffic.latitude as int) = cast(BusStop.latitude as int) AND cast(Traffic.longitude as int) = cast(BusStop.longitude as int)
    )
    SELECT the_date, the_time, stop_number, longitude, latitude
    FROM RankedStops
    WHERE traffic_rank = 1 OR traffic_rank = (SELECT COUNT(DISTINCT traffic_rank) FROM RankedStops);
  ''')
  result = cursor.fetchall()
    
  # Get the column names from cursor description
  columns = [column[0] for column in cursor.description]
    
  return render_template('display.html', columns=columns, result=result)
# ====================================================================================================
# ====================================================================================================
@app.route('/query10', methods=['POST'])
def query10():
  cursor = conn.cursor()
  cursor.execute('''
    WITH BestWeatherLowTraffic AS (
      SELECT top 1 Weather.the_date, Weather.max_temp, Weather.min_temp, Weather.total_precip_mm, Weather.snow_on_grnd_cm, Traffic.total
      FROM Weather
      JOIN Traffic ON Weather.the_date = Traffic.the_date
      ORDER BY (Traffic.total / (Weather.max_temp - Weather.min_temp + 1)) ASC
    )
    SELECT the_date, max_temp, min_temp, total_precip_mm, snow_on_grnd_cm, total
    FROM BestWeatherLowTraffic;
  ''')
  result = cursor.fetchall()
    
  # Get the column names from cursor description
  columns = [column[0] for column in cursor.description]
    
  return render_template('display.html', columns=columns, result=result)
# ====================================================================================================
# ====================================================================================================
@app.route('/query11', methods=['POST'])
def query11():
  cursor = conn.cursor()
  cursor.execute('''
    DECLARE @SelectedRouteNumber NVARCHAR(50) = '60'; 

    SELECT
        @SelectedRouteNumber AS selected_route,
        CASE
            WHEN @SelectedRouteNumber IS NULL THEN 'All Routes'
            ELSE 'BLUE'
        END AS aggregation_type,
        AVG(deviation) AS average_deviation
    FROM Arrival
    WHERE
        @SelectedRouteNumber IS NULL OR
        (route_number = @SelectedRouteNumber);
  ''')
  result = cursor.fetchall()
    
  # Get the column names from cursor description
  columns = [column[0] for column in cursor.description]
    
  return render_template('display.html', columns=columns, result=result)
# ====================================================================================================

if __name__ == '__main__':
  host_name = socket.gethostname()
  app.run(debug=True)
