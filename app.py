from flask import Flask, render_template, jsonify, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func
import os

database_url = os.getenv('DATABASE_URL')

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url.replace('postgres://', 'postgresql://', 1)
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
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    participants = db.Column(db.ARRAY(db.Numeric(9, 6)), nullable=True)
    creator = db.relationship('Users', backref='activities')

class Users(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(50), nullable=False)

def get_route(marker):
    lat_lon_pairs = zip(marker.route_lat, marker.route_lon)
    route = [[float(lat), float(lon)] for lat, lon in lat_lon_pairs]
    return route

def generate_output(markers):
    return jsonify({'markers': [{'id' : marker.id,
                                 'title': marker.activity_type,
                                 'lat': marker.start_lat,
                                 'lon': marker.start_lon,
                                 'short_description':marker.short_description,
                                 'start_at':marker.start_at,
                                 'estimated_duration_minutes':marker.estimated_duration_minutes,
                                 'created_by':marker.creator.first_name + ' ' + marker.creator.last_name,
                                 'details_url': url_for('marker_details', marker_id=marker.id)
                                 } for marker in markers]})


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
            markers = Marker.query.join(Users, Marker.created_by == Users.id).filter(Marker.start_lat >= sw_lat, Marker.start_lat <= ne_lat,
                                          Marker.start_lon >= sw_lon, Marker.start_lon <= ne_lon).order_by(func.random()).limit(10).all()
        else:
            markers = Marker.query.join(Users, Marker.created_by == Users.id).order_by(func.random()).limit(10).all()
        print([m for m in markers])
        return generate_output(markers)
    else:
        markers = Marker.query.join(Users, Marker.created_by == Users.id).order_by(func.random()).limit(10).all()
        return generate_output(markers)

@app.route('/marker_details/<int:marker_id>')
def marker_details(marker_id):
    # Get Marker data from the database using marker_id
    marker = Marker.query.filter_by(id=marker_id).first()
    participants_ids = marker.participants
    participants = Users.query.filter(Users.id.in_(participants_ids)).all()
    participant_names = [p.first_name + ' ' + p.last_name for p in participants]
    participant_phones = [p.phone for p in participants]
    participant_emails = [p.email for p in participants]
    participants = {
        'name':participant_names
    }
    # Get route from Marker data
    route = get_route(marker)
    print(route)

    # Render HTML template with Marker data
    return render_template('marker_details.html',
                           lat=marker.start_lat,
                           lon=marker.start_lon,
                           route=route,
                           short_description=marker.short_description,
                           start_time=marker.start_at.strftime('%Y-%m-%d %H:%M:%S'),
                           estimated_duration=marker.estimated_duration_minutes,
                           participant_names=participant_names,
                           participant_phones=participant_phones,
                           participant_emails=participant_emails,
                           )


if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)
