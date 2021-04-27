from flask import Flask
from flask import render_template
from flask import request
from flask import flash, redirect
import requests as r
import json
from flask_sqlalchemy import SQLAlchemy
import sys

app = Flask(__name__)
api_key = '2f6ba15d16cb9b95589451040cd975c6'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.secret_key = "qwerty"
db = SQLAlchemy(app)


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), unique=True, nullable=False)

    def __repr__(self):
        return f'{self.name} {self.id}'


db.create_all()

weather_list = []


def weather_list_creator():
    global weather_list
    weather_list = []
    for city in City.query.all():
        city_id = str(city).split()[1]
        city = str(city).split()[0]
        weather_info = r.get(f'http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={api_key}')
        weather_info = weather_info.json()
        city_info = {'name': weather_info['name'], 'temp': weather_info['main']['temp'],
                                'state': weather_info['weather'][0]['main'], 'id': int(city_id)}
        weather_list.append(city_info)


@app.route('/')
def index():
    weather_list_creator()
    return render_template('index.html', data=weather_list)


@app.route('/add', methods=['GET', 'POST'])
def add_city():
    city = ''.join(request.form.getlist('city_name'))
    if city == '':
        return redirect('/')
    else:
        if city not in str(City.query.filter_by(name=city).first()).split()[0]:
            weather_info = r.get(
                f'http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={api_key}')
            if weather_info.status_code == 200:
                city_test = City(name=city)
                db.session.add(city_test)
                db.session.commit()
            else:
                flash("The city doesn't exist!")
        else:
            flash("The city has already been added to the list!")
    return redirect('/')


@app.route('/delete/<city_id>', methods=['GET', 'POST'])
def delete(city_id):
    city = City.query.filter_by(id=city_id).first()
    db.session.delete(city)
    db.session.commit()
    return redirect('/')


# don't change the following way to run flask:
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()
