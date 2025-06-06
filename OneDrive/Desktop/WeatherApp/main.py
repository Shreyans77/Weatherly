from flask import Flask, request, render_template, flash, redirect, url_for
import requests
import datetime
import os

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'd7e94f6a2c8b4e9f93a1d2c7b4f5a6e1')

OPENWEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY', '4f7b5e2ce730121fb005a50904372f80')
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY', 'AIzaSyC47c9GsxF-Yjo3H8fWb2ANr6qd6-4dM88')
GOOGLE_CSE_ID = os.environ.get('GOOGLE_CSE_ID', 'a2c23c1fa75934007')

def kelvin_to_celsius(kelvin):
    return kelvin - 273.15

def format_time(timestamp, timezone_offset=0):
    # Convert UNIX timestamp to readable time with timezone offset
    dt = datetime.datetime.utcfromtimestamp(timestamp + timezone_offset)
    return dt.strftime('%I:%M %p')

@app.route("/")
def index():
    # Show default city weather, or blank form
    return render_template('index.html')

@app.route("/pred", methods=['POST'])
def pred():
    city = request.form.get('city', '').strip()
    if not city:
        flash("Please enter a city name.", "warning")
        return redirect(url_for('index'))

    weather_url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric'
    response = requests.get(weather_url)
    data = response.json()

    if response.status_code != 200 or 'main' not in data:
        flash("Could not fetch weather data for the city. Please check the city name.", "danger")
        return redirect(url_for('index'))

    # Extract relevant data
    weather = data['weather'][0]
    main = data['main']
    wind = data.get('wind', {})
    clouds = data.get('clouds', {})
    sys = data.get('sys', {})
    timezone_offset = data.get('timezone', 0)

    description = weather.get('description', '').title()
    icon = weather.get('icon', '01d')
    temp = main.get('temp')
    humidity = main.get('humidity')
    wind_speed = wind.get('speed')
    max_temp = main.get('temp_max')
    min_temp = main.get('temp_min')
    pressure = main.get('pressure')
    precipitation = data.get('rain', {}).get('1h', 0)  # rain volume for last 1h (if available)
    cloudiness = clouds.get('all')
    sunrise = format_time(sys.get('sunrise', 0), timezone_offset)
    sunset = format_time(sys.get('sunset', 0), timezone_offset)
    day = datetime.datetime.utcnow().strftime('%A, %B %d, %Y')

    # Alerts
    hot_alert = "It's very hot today! Stay hydrated and avoid direct sun exposure." if temp and temp >= 40 else None
    cold_alert = "It's cold today! Dress warmly." if temp and temp <= 10 else None

    # Google Custom Search API for city image
    query = f"{city} cityscape 1920x1080"
    google_url = (
        f"https://www.googleapis.com/customsearch/v1?"
        f"key={GOOGLE_API_KEY}&cx={GOOGLE_CSE_ID}&q={query}&searchType=image&imgSize=xxlarge&num=1"
    )
    image_resp = requests.get(google_url).json()
    image_url = image_resp.get("items", [{}])[0].get("link", url_for('static', filename='default_bg.jpg'))

    return render_template(
        'index.html',
        city=city.title(),
        description=description,
        icon=icon,
        temp=temp,
        humidity=humidity,
        wind_speed=wind_speed,
        max_temp=max_temp,
        min_temp=min_temp,
        pressure=pressure,
        precipitation=precipitation,
        cloudiness=cloudiness,
        sunrise=sunrise,
        sunset=sunset,
        day=day,
        hot_alert=hot_alert,
        cold_alert=cold_alert,
        image_url=image_url
    )


if __name__ == "__main__":
    app.run(debug=True)
