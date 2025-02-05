from flask import Flask, request, jsonify, render_template
import swisseph as swe
import datetime

app = Flask(__name__)

# Function to compute Kundali
def calculate_kundali(year, month, day, hour, minute, lat, lon, tz):
    julian_day = swe.julday(year, month, day, hour + minute / 60.0 - tz)
    
    planets = {
        "Sun": swe.SUN, "Moon": swe.MOON, "Mercury": swe.MERCURY, "Venus": swe.VENUS,
        "Mars": swe.MARS, "Jupiter": swe.JUPITER, "Saturn": swe.SATURN,
        "Rahu": swe.MEAN_NODE, "Ketu": swe.MEAN_NODE
    }

    planet_positions = {}
    for planet, pid in planets.items():
        pos, _ = swe.calc_ut(julian_day, pid)
        planet_positions[planet] = pos[0]  # Longitude in degrees

    # Compute Lagna (Ascendant)
    ascendant_info = swe.houses(julian_day, lat, lon, b'A')
    lagna_degree = ascendant_info[0][0]  # Extract only the first value (Ascendant degree)
    lagna_house = ((int(lagna_degree // 30) + 1) % 12) + 1  # Convert to house number

    # Compute Moon sign for Janma Kundali
    moon_degree = planet_positions["Moon"]
    moon_sign = ((int(moon_degree // 30) + 1) % 12) + 1  # Convert to house number

    # Assign planets to houses for Janma Kundali (Moon-based)
    janma_houses = {i: [] for i in range(1, 13)}
    for planet, degrees in planet_positions.items():
        house_num = ((int(degrees // 30) + 1 - moon_sign) % 12) + 1
        janma_houses[house_num].append(planet)

    # Assign planets to houses for Lagna Kundali (Ascendant-based)
    lagna_houses = {i: [] for i in range(1, 13)}
    for planet, degrees in planet_positions.items():
        house_num = ((int(degrees // 30) + 1 - lagna_house) % 12) + 1
        lagna_houses[house_num].append(planet)

    return {"lagna": lagna_house, "janma_houses": janma_houses, "lagna_houses": lagna_houses}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    kundali = calculate_kundali(
        int(data["year"]), int(data["month"]), int(data["day"]),
        int(data["hour"]), int(data["minute"]),
        float(data["lat"]), float(data["lon"]), float(data["tz"])
    )
    return jsonify(kundali)

if __name__ == "__main__":
    app.run(debug=True)
