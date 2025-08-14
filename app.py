from flask import Flask, render_template, request, redirect, flash, session, url_for
import csv
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flash messages

CSV_FILE = 'check_log.csv'

USERNAME = 'admin'  
PASSWORD = 'password'  

@app.route('/check-in', methods=['POST'])
def check_in():
    guest_name = request.form.get('guest_name').strip().lower()
    reason_for_visit = request.form.get('reason_for_visit')
    who_meeting = request.form.get('who_meeting')

    if not guest_name or not reason_for_visit or not who_meeting:
        flash("Please enter all fields.")
        return redirect('/')

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if len(guest_name) > 32 or len(reason_for_visit) > 64 or len(who_meeting) > 32:
        flash("Input exceeds maximum length.")
        return redirect('/')

    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([guest_name, reason_for_visit, who_meeting, timestamp, "Check In", ""])

    flash(f"{guest_name} checked in at {timestamp}")
    return redirect('/')

@app.route('/check-out', methods=['POST'])
def check_out():
    guest_name = request.form.get('guest_name').strip().lower()
    

    if not guest_name:
        flash("Please enter Guest Name for check out.")
        return redirect('/')

    rows = []
    found = False

    if not os.path.exists(CSV_FILE):
        flash("Check log not found.")
        return redirect('/')

    with open(CSV_FILE, "r", newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)

    for i in range(len(rows) - 1, -1, -1):
        if rows[i][0] == guest_name and rows[i][4] == "Check In" and not rows[i][5]:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            rows[i][5] = timestamp
            rows[i][4] = "Check Out"
            found = True
            break

    if found:
        with open(CSV_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(rows)
        flash(f"Guest {guest_name} checked out.")
    else:
        flash("No active check-in found for this Guest.")

    return redirect('/')

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            flash("Login successful!")
            return redirect('/')
        else:
            flash("Invalid credentials. Please try again.")
            return redirect('/login')

    return render_template('login.html')
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash("You have been logged out.")
    return redirect('/')

@app.route('/view-log', methods=['GET'])
def view_log():
    if not session.get('logged_in'):
        flash("You must be logged in to view the log.")
        return redirect('/')
    
    rows = []
    show_all = request.args.get('show_all')
    search_query = request.args.get('search', '').strip().lower()

    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'r', newline='') as f:
            reader = csv.reader(f)
            all_rows = list(reader)

            data_rows = all_rows

            if search_query:
                data_rows = [
                    row for row in data_rows
                    if any(search_query in (col or '').lower() for col in row)
                ]
            elif not show_all:
                data_rows = [
                    row for row in data_rows
                    if len(row) >= 6 and row[4] == "Check In" and not row[5].strip()
                ]
            rows = data_rows

    return render_template('view_log.html', rows=rows, show_all=show_all)
# @app.route('/clear-log', methods=['POST'])
# def clear_log():
#     if not session.get('logged_in'):
#         flash("You must be logged in to clear the log.")
#         return redirect('/login')

#     open(CSV_FILE, 'w').close()
#     flash("Log cleared successfully.")

#     return redirect('/view-log')
if __name__ == '__main__':
    app.run(debug=True)
