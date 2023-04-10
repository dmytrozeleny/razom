from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:w5MkULrRIquRYlh@localhost:5432/razom_db"
db = SQLAlchemy(app)

class Marker(db.Model):
    __tablename__ = 'sports_activities'

    id = db.Column(db.Integer, primary_key=True)
    activity_type = db.Column(db.String(50), nullable=False)
    estimated_duration_minutes = db.Column(db.Integer, nullable=False)
    start_lat = db.Column(db.Numeric(9, 6), nullable=False)
    start_lon = db.Column(db.Numeric(9, 6), nullable=False)
    route_lat = db.Column(db.ARRAY(db.Numeric(9, 6)), nullable=True)
    route_lon = db.Column(db.ARRAY(db.Numeric(9, 6)), nullable=True)
    start_at = db.Column(db.DateTime(timezone=True), nullable=False)
    short_description = db.Column(db.String(100), nullable=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/markers', methods=['GET', 'POST'])
def get_markers():
    if request.method == 'POST':
        boundaries = request.get_json()
        if boundaries:
            sw_lat, sw_lon = boundaries['sw_lat'], boundaries['sw_lon']
            ne_lat, ne_lon = boundaries['ne_lat'], boundaries['ne_lon']
            markers = Marker.query.filter(Marker.start_lat >= sw_lat, Marker.start_lat <= ne_lat,
                                          Marker.start_lon >= sw_lon, Marker.start_lon <= ne_lon).limit(10).all()
        else:
            markers = Marker.query.limit(10).all()
        return jsonify({'markers': [{'title': marker.activity_type,
                                     'lat': marker.start_lat,
                                     'lon': marker.start_lon,
                                     'short_description':marker.short_description,
                                     'start_at':marker.start_at,
                                     'estimated_duration_minutes':marker.estimated_duration_minutes
                                     } for marker in markers]})
    else:
        markers = Marker.query.limit(10).all()
        return jsonify({'markers': [{'title': marker.activity_type,
                                     'lat': marker.start_lat,
                                     'lon': marker.start_lon,
                                     'short_description':marker.short_description,
                                     'start_at':marker.start_at,
                                     'estimated_duration_minutes':marker.estimated_duration_minutes
                                     } for marker in markers]})
    
@app.route('/event_details/<event_id>')
def about():
  return render_template("about.html")


if __name__ == '__main__':
    app.run(debug=True)