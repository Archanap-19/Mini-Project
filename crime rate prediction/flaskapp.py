from flask import Flask, request, render_template, redirect, url_for, session
import pickle
import math

app = Flask(__name__)
app.secret_key = "secret_key_for_session"  # Change this to a secure random key

# Load trained model
model = pickle.load(open('model.pkl', 'rb'))

# Dummy users (in-memory)
users = {"admin": "admin123", "user": "password"}


# ===============================
# Home Route
# ===============================
@app.route('/')
def home():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("crindex.html")


# ===============================
# Login Route
# ===============================
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username in users and users[username] == password:
            session["logged_in"] = True
            session["username"] = username
            return redirect(url_for("home"))
        else:
            return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")


# ===============================
# Register Route
# ===============================
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username in users:
            return render_template("register.html", error="Username already exists!")
        elif not username or not password:
            return render_template("register.html", error="Please fill all fields!")
        else:
            users[username] = password
            return render_template("register.html", success="Registration successful! You can now log in.")
    return render_template("register.html")


# ===============================
# Logout Route
# ===============================
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("login"))


# ===============================
# Prediction Route
# ===============================
@app.route('/predict', methods=['POST'])
def predict_result():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    city_names = {
        '0': 'Ahmedabad', '1': 'Bengaluru', '2': 'Chennai', '3': 'Coimbatore', '4': 'Delhi',
        '5': 'Ghaziabad', '6': 'Hyderabad', '7': 'Indore', '8': 'Jaipur', '9': 'Kanpur',
        '10': 'Kochi', '11': 'Kolkata', '12': 'Kozhikode', '13': 'Lucknow', '14': 'Mumbai',
        '15': 'Nagpur', '16': 'Patna', '17': 'Pune', '18': 'Surat'
    }

    crimes_names = {
        '0': 'Crime Committed by Juveniles', '1': 'Crime against SC', '2': 'Crime against ST',
        '3': 'Crime against Senior Citizen', '4': 'Crime against children', '5': 'Crime against women',
        '6': 'Cyber Crimes', '7': 'Economic Offences', '8': 'Kidnapping', '9': 'Murder'
    }

    population = {
        '0': 63.50, '1': 85.00, '2': 87.00, '3': 21.50, '4': 163.10, '5': 23.60, '6': 77.50,
        '7': 21.70, '8': 30.70, '9': 29.20, '10': 21.20, '11': 141.10, '12': 20.30, '13': 29.00,
        '14': 184.10, '15': 25.00, '16': 20.50, '17': 50.50, '18': 45.80
    }

    city_code = request.form["city"]
    crime_code = request.form["crime"]
    year = request.form["year"]

    pop = population[city_code]
    year_diff = int(year) - 2011
    pop = pop + 0.01 * year_diff * pop

    crime_rate = model.predict([[int(year), int(city_code), pop, int(crime_code)]])[0]

    city_name = city_names[city_code]
    crime_type = crimes_names[crime_code]

    if crime_rate <= 1:
        crime_status = "Very Low Crime Area"
        alert_message = "✅ Safe for tourists. Usual precautions recommended."
        alert_type = "success"
    elif crime_rate <= 5:
        crime_status = "Low Crime Area"
        alert_message = "✅ Relatively safe. Normal safety measures advised."
        alert_type = "info"
    elif crime_rate <= 15:
        crime_status = "High Crime Area"
        alert_message = "⚠️ High crime area. Avoid travelling alone at night."
        alert_type = "warning"
    else:
        crime_status = "Very High Crime Area"
        alert_message = "🚨 Very high crime risk! Avoid unsafe areas and stay alert."
        alert_type = "danger"

    cases = math.ceil(crime_rate * pop)

    return render_template(
        'crresult.html',
        city_name=city_name,
        crime_type=crime_type,
        year=year,
        crime_status=crime_status,
        crime_rate=round(crime_rate, 2),
        cases=cases,
        population=round(pop, 2),
        alert_message=alert_message,
        alert_type=alert_type
    )


# ===============================
# Run Flask (Manual Start Only)
# ===============================
if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
