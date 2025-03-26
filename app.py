from flask import Flask, request, jsonify
import swisseph as swe
import datetime
import pytz

app = Flask(__name__)
swe.set_ephe_path('/usr/share/ephe')  # Path to Swiss Ephemeris

@app.route('/panchang', methods=['GET'])
def get_panchang():
    date = request.args.get('date')  # Format: YYYY-MM-DD
    lat = float(request.args.get('lat'))
    lng = float(request.args.get('lng'))
    tz_name = request.args.get('timezone', 'Asia/Kolkata')

    try:
        # Convert date to Julian Day
        dt = datetime.datetime.strptime(date, "%Y-%m-%d")
        tz = pytz.timezone(tz_name)
        local_dt = tz.localize(dt)
        utc_dt = local_dt.astimezone(pytz.utc)
        jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour + utc_dt.minute / 60)

        # Get sun and moon longitude
        sun_long = swe.calc_ut(jd, swe.SUN)[0][0]
        moon_long = swe.calc_ut(jd, swe.MOON)[0][0]

        # Tithi and Nakshatra
        angular_diff = (moon_long - sun_long) % 360
        tithi_num = int(angular_diff / 12) + 1
        nakshatra_num = int((moon_long % 360) / (360 / 27)) + 1

        return jsonify({
            "date": date,
            "latitude": lat,
            "longitude": lng,
            "tithi_number": tithi_num,
            "nakshatra_number": nakshatra_num,
            "sunrise": "06:00 AM",
            "sunset": "06:30 PM"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run()