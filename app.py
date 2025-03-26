from flask import Flask, request, jsonify
from skyfield.api import load
from datetime import datetime
import pytz

app = Flask(__name__)

def calculate_tithi(moon_lon, sun_lon):
    angle = (moon_lon - sun_lon) % 360
    tithi = int(angle // 12) + 1
    return tithi

def calculate_nakshatra(moon_lon):
    nakshatra = int((moon_lon % 360) // (360 / 27)) + 1
    return nakshatra

@app.route('/panchang')
def get_panchang():
    try:
        date_str = request.args.get('date')
        lat = float(request.args.get('lat'))
        lng = float(request.args.get('lng'))
        timezone = request.args.get('timezone', 'Asia/Kolkata')

        eph = load('de421.bsp')
        ts = load.timescale()
        tz = pytz.timezone(timezone)
        local_dt = tz.localize(datetime.strptime(date_str, '%Y-%m-%d'))
        utc_dt = local_dt.astimezone(pytz.utc)
        t = ts.utc(utc_dt.year, utc_dt.month, utc_dt.day)

        sun = eph['sun']
        moon = eph['moon']
        earth = eph['earth']

        astrometric_sun = earth.at(t).observe(sun).apparent()
        astrometric_moon = earth.at(t).observe(moon).apparent()

        sun_lon, _, _ = astrometric_sun.ecliptic_latlon()
        moon_lon, _, _ = astrometric_moon.ecliptic_latlon()

        tithi = calculate_tithi(moon_lon.degrees, sun_lon.degrees)
        nakshatra = calculate_nakshatra(moon_lon.degrees)

        sunrise = "06:00 AM"
        sunset = "06:30 PM"

        return jsonify({
            "date": date_str,
            "latitude": lat,
            "longitude": lng,
            "tithi_number": tithi,
            "nakshatra_number": nakshatra,
            "sunrise": sunrise,
            "sunset": sunset
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run()
