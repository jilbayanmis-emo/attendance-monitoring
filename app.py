from flask import Flask, render_template_string, request, redirect, url_for, session
import pandas as pd
import csv
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "yoursecretkey"  # 🔐 change this to a random string
members_file = "members.xlsx"


# Load members from Excel
def load_members():
	return pd.read_excel(members_file)

# Save members to Excel
def save_members(df):
	df.to_excel(members_file, index=False)

# Load attendance from CSV
def load_attendance():
	if not os.path.exists("attendance.csv"):
		return []
	df = pd.read_csv("attendance.csv")
	return df.to_dict(orient="records")

# Dropdown options
NETWORKS = [
	"Children - Girls", "Children - Boys",
	"KKB - Boys", "KKB - Girls",
	"YAN - Boys", "YAN - Girls",
	"Men", "Women"
]

TRIBES = [
	"HABAKKUK","JOHN THE BELOVED","CORNELIUS","DANIEL","JOSHUA","CALEB","ELISHA","STEPHEN","JOB","GIDEON","MARCOS",
	"DAVID","ABIGAIL","LOIS","MARY TRIBE","DEBORAH","ESTHER","SARAH TRIBE","NAOMI","ELIZABETH","LYDIA","HANNAH",
	"EMMANUEL","KEZIAH","ZAMARA","APPHIA","RACHEL","SUSANA","MIRIAM","LEAH","PHOEBE","ZIPORRAH","EDEN"
]

LEADERS = [
	"Ptra. Rodilyn Evangelista", "Joel Evangelista", "Alezandrei Jamil Almeda","Arjay Pantilon","Dale Exel Aramay","Domel Anito","Federico Bacsal","Henry Cabal",
	"Isaiah Mark Alen Pantilon","John Anthony Abarra","John Cesar San Juan","Leo Olipane","Roger Fallorin","Romy David",
	"Annabelle Dejesa","Ashley Jeane Ocampo","Divine Medrano","Dolor Bacsal","Evelyn Pantilon","Angelita Draguin",
	"Margarette Pantilon","Marites Fallorin","Nathasha Payumo","Noemi Cabal","Shara Mae Laguatan","Shekinah Shine Evangelista",
	"Roajean Sarmiento","Deanne Es Ignacio","Apple Mirando","Lerma David","Elizabeth Mora","Aileen Batara","Ella Olipane",
	"Sheron Love Payumo","Geal Payumo"
]

SOURCES = ["WSAM-LGAM", "WSAM", "LGAM", "ATTENDEE", "First Timer", "Visitor"]

@app.route("/")
def index():
	return redirect(url_for("login"))


# ----------------- Login Page -----------------
@app.route("/login", methods=["GET", "POST"])
def login():
	error = None
	if request.method == "POST":
		username = request.form["username"]
		password = request.form["password"]

		# ✅ Replace this with your actual username & password
		if username == "admin" and password == "jtrkemo":
			session["logged_in"] = True
			return redirect(url_for("home"))
		else:
			error = "❌ User not found or wrong password!"

	return render_template_string("""
		<head>
		  <meta name="viewport" content="width=device-width, initial-scale=1">
		  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
		</head>
		<style>
	body {  background-image: url('{{ url_for("static", filename="background.png") }}'); background-size: cover; background-position: center; background-repeat: no-repeat; background-attachment: fixed; font-family:"Georgia","Times New Roman", serif; color:#fff;
	}
	/* Optional: overlay to make text readable */
		body::before {	content: ""; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.4);  /* Adjust darkness */
		z-index: -1;
		}
	</style>
		<div class="container mt-5">
		  <div class="row justify-content-center">
			<div class="col-md-4">
			  <div class="card shadow-lg p-4">
				<h2 class="text-center mb-4">🔑 Login</h2>
				<form method="POST">
				  <div class="mb-3">
					<label class="form-label">Username</label>
					<input type="text" name="username" class="form-control" required>
				  </div>
				  <div class="mb-3">
					<label class="form-label">Password</label>
					<input type="password" name="password" class="form-control" required>
				  </div>
				  <button type="submit" class="btn btn-primary w-100">Login</button>
				</form>

				{% if error %}
				  <div class="alert alert-danger text-center mt-3">{{ error }}</div>
				{% endif %}
			  </div>
			</div>
		  </div>
		</div>
	""", error=error)


# ----------------- Logout Page -----------------
@app.route("/logout")
def logout():
	session.pop("logged_in", None)
	return redirect(url_for("login"))

# ----------------- Home Page -----------------
@app.route("/home", methods=["GET", "POST"])
def home():
	if "logged_in" not in session:
		return redirect(url_for("login"))
	members = load_members().to_dict(orient="records")
	services = ["Morning Service", "Evening Service", "Worship Extension Service (WES)", "Other Day Service"]

	success = None
	error = None

	if request.method == "POST":
		name = (request.form.get("member") or "").strip()
		service = (request.form.get("Service") or "").strip()

		if not name or not service:
			error = "❌ Please select your name and a service."
		else:
			member = next((m for m in members if m["Name"] == name), None)

			if member:
				df_att = pd.DataFrame(load_attendance())

				# check if already attended
				if not df_att.empty and ((df_att["Name"] == name) & (df_att["Service"] == service)).any():
					error = (
							f"❌ {name} has already attended {service}!<br>"
							f"Network: {member['Network']}<br>"
							f"Tribe: {member['Tribe/Clan']}<br>"
							f"Leader: {member['Tribe/Lifegroup Leader']}"
						)

				else:
					# record attendance
					timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
					file_exists = os.path.isfile("attendance.csv")
					with open("attendance.csv", "a", newline="", encoding="utf-8") as f:
						writer = csv.writer(f)
						if not file_exists:
							writer.writerow([
								"Name", "Network", "Tribe/Clan", "Tribe/Lifegroup Leader",
								"Source of Membership", "Service", "Timestamp"
							])
						writer.writerow([
							member["Name"], member["Network"], member["Tribe/Clan"],
							member["Tribe/Lifegroup Leader"], member["Source of Membership"],
							service, timestamp
						])
					success = f"""
					✅ Attendance recorded for {name} at {service}!<br>
					<b>Network:</b> {member['Network']}<br>
					<b>Tribe:</b> {member['Tribe/Clan']}<br>
					<b>Leader:</b> {member['Tribe/Lifegroup Leader']}
					"""
			else:
				error = f"❌ Member <b>{name}</b> not found! Please check spelling or add them first."


	return render_template_string("""
	<!DOCTYPE html>
	<html lang="en">
	<head>
		<meta charset="UTF-8">
		<meta name="viewport" content="width=device-width, initial-scale=1">
		<title>Church Attendance System</title>
		<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
		<style>
			body {  
				background-image: url('{{ url_for("static", filename="background.png") }}');
				background-size: cover;
				background-position: center;
				background-repeat: no-repeat;
				background-attachment: fixed;
				font-family:"Georgia","Times New Roman", serif;
				color:#fff;
			}
			body::before {	
				content: ""; position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
				background-color: rgba(0,0,0,0.4);
				z-index: -1;
			}
			.container-card { max-width:450px; margin:60px auto; padding:30px; background:#fff; border-radius:12px; 
							  box-shadow:0 6px 20px rgba(0,0,0,0.1); text-align:center; color:#000; }
			h2 { margin-bottom:25px; font-weight:bold; }
			input, select { margin-bottom:15px; height:45px; font-family:inherit; }
			button { width:100%; padding:10px; font-weight:bold; font-family:inherit; }
			.links a { margin:5px; }
			img.logo { width:120px; height:120px; border-radius:50%; display:block; margin:0 auto 20px; 
					   box-shadow:0 4px 10px rgba(0,0,0,0.2); }
		</style>
	</head>
	<body>
		<div class="container-card">
			<img src="{{ url_for('static', filename='JIL-Iba-Bayan.png') }}" class="logo" alt="Church Logo">
			<h2>Church Attendance Monitoring</h2>
			<form method="POST">
				<input type="text" id="member" name="member" list="members_list" class="form-control" placeholder="Start typing your name..." required>
				<datalist id="members_list">
					{% for m in members %}<option value="{{ m['Name'] }}">{% endfor %}
				</datalist>
				<label>Services:</label>
				<select name="Service" class="form-select" required>
					{% for srv in services %}<option value="{{ srv }}">{{ srv }}</option>{% endfor %}
				</select>
				<button type="submit" class="btn btn-primary mt-2">Submit</button>
			</form>

				{% if error %}
				  <div class="alert alert-danger">
					{{ error|safe }}
				  </div>
				{% endif %}

				{% if success %}
				  <div class="alert alert-success">
					{{ success|safe }}
				  </div>
				{% endif %}

			<div class="links mt-3">
				<a href="/attendance" class="btn btn-outline-secondary btn-sm">📊 View Attendance Logs</a>
				<a href="/members" class="btn btn-outline-secondary btn-sm">📋 List of Membership</a>
				<a href="/add_member" class="btn btn-outline-secondary btn-sm">➕ Add Member</a>
				<a href="{{ url_for('logout') }}" class="btn btn-danger">Logout</a>
			</div>
		</div>
	</body>
	</html>
	""", members=members, services=services, error=error, success=success)



# ----------------- Attendance Page -----------------

@app.route("/attendance", methods=["GET", "POST"])
def attendance():
	if "logged_in" not in session:
		return redirect(url_for("login"))

	df = pd.DataFrame(load_attendance())
	services = ["Morning Service", "Evening Service", "Other Day Service", "Worship Extension Service (WES)"]
	if df.empty:
		return render_template_string("""<!DOCTYPE html>
		<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
		<title>Attendance Logs</title>
		<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
		<style>body {  
				background-image: url('{{ url_for("static", filename="background.png") }}');
				background-size: cover;
				background-position: center;
				background-repeat: no-repeat;
				background-attachment: fixed;
				font-family:"Georgia","Times New Roman", serif;
				color:#fff;
			}
			body::before {	
				content: ""; position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
				background-color: rgba(0,0,0,0.4);
				z-index: -1;
			}
		.container-card { max-width:900px; margin:40px auto; padding:20px; background:#fff; border-radius:12px; box-shadow:0 6px 20px rgba(0,0,0,0.1); color:#000; }
		h2 { text-align:center; margin-bottom:20px; font-weight:bold; }</style></head>
		<body><div class="container-card">
		<h2>📊 Attendance Logs</h2>
		<p>No attendance recorded yet.</p>
		<a href="/" class="btn btn-outline-secondary">⬅ Back to Home</a>
		</div></body></html>""")

	# Filter selections
	selected_network = request.form.get("Network", "All")
	selected_tribe = request.form.get("TribeClan", "All")
	selected_source = request.form.get("Source", "All")
	selected_service = request.form.get("Service", "All")

	filtered_df = df.copy()
	if selected_network != "All": filtered_df = filtered_df[filtered_df["Network"].str.lower() == selected_network.lower()]
	if selected_tribe != "All": filtered_df = filtered_df[filtered_df["Tribe/Clan"].str.lower() == selected_tribe.lower()]
	if selected_source != "All": filtered_df = filtered_df[filtered_df["Source of Membership"].str.lower() == selected_source.lower()]
	if selected_service != "All": filtered_df = filtered_df[filtered_df["Service"].str.lower() == selected_service.lower()]

	# Count unique attendees
	total_filtered = filtered_df["Name"].nunique()

	return render_template_string("""
	<!DOCTYPE html>
	<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
	<title>Attendance Logs</title>
	<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
	<style>body {  
				background-image: url('{{ url_for("static", filename="background.png") }}');
				background-size: cover;
				background-position: center;
				background-repeat: no-repeat;
				background-attachment: fixed;
				font-family:"Georgia","Times New Roman", serif;
				color:#fff;
			}
			body::before {	
				content: ""; position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
				background-color: rgba(0,0,0,0.4);
				z-index: -1;
			}
	.container-card { max-width:1100px; margin:40px auto; padding:20px; background:#fff; border-radius:12px; box-shadow:0 6px 20px rgba(0,0,0,0.1); color:#000; }
	h2 { text-align:center; margin-bottom:20px; font-weight:bold; } table { margin-top:20px; width:100%; } select, button { height:45px; margin-right:5px; margin-bottom:10px; }</style></head>
	<body><div class="container-card">
	<h2>📊 Attendance Logs</h2>

	<!-- Filter Form -->
	<form method="POST" class="d-flex flex-wrap align-items-end">
		<div class="me-2">
			<label><b>Network:</b></label>
			<select name="Network" class="form-select">
				<option value="All">All</option>
				{% for n in networks %}<option value="{{ n }}" {% if n.lower() == selected_network.lower() %}selected{% endif %}>{{ n }}</option>{% endfor %}
			</select>
		</div>
		<div class="me-2">
			<label><b>Tribe/Clan:</b></label>
			<select name="TribeClan" class="form-select">
				<option value="All">All</option>
				{% for t in tribes %}<option value="{{ t }}" {% if t.lower() == selected_tribe.lower() %}selected{% endif %}>{{ t }}</option>{% endfor %}
			</select>
		</div>
		<div class="me-2">
			<label><b>Source:</b></label>
			<select name="Source" class="form-select">
				<option value="All">All</option>
				{% for s in sources %}<option value="{{ s }}" {% if s.lower() == selected_source.lower() %}selected{% endif %}>{{ s }}</option>{% endfor %}
			</select>
		</div>
		<div class="me-2">
			<label><b>Service:</b></label>
			<select name="Service" class="form-select">
				<option value="All">All</option>
				{% for srv in services %}<option value="{{ srv }}" {% if srv.lower() == selected_service.lower() %}selected{% endif %}>{{ srv }}</option>{% endfor %}
			</select>
		</div>
		<button type="submit" class="btn btn-primary">🔍 Apply Filter</button>
	</form>

	<p><b>Total Unique Attendees:</b> {{ total_filtered }}</p>

	<div class="table-responsive">
		<table class="table table-striped table-bordered">
			<thead>
				<tr>
					<th>Name</th><th>Network</th><th>Tribe/Clan</th><th>Tribe/Lifegroup Leader</th>
					<th>Source of Membership</th><th>Service</th><th>Timestamp</th>
				</tr>
			</thead>
			<tbody>
				{% for i,row in filtered_df.iterrows() %}
				<tr>
					<td>{{ row['Name'] }}</td>
					<td>{{ row['Network'] }}</td>
					<td>{{ row['Tribe/Clan'] }}</td>
					<td>{{ row['Tribe/Lifegroup Leader'] }}</td>
					<td>{{ row['Source of Membership'] }}</td>
					<td>{{ row['Service'] }}</td>
					<td>{{ row['Timestamp'] }}</td>
				</tr>
				{% endfor %}
			</tbody>
		</table>
	</div>

	<a href="/home" class="btn btn-outline-secondary mt-3">⬅ Back to Home</a>
	</div></body></html>
	""", filtered_df=filtered_df, total_filtered=total_filtered,
	   networks=NETWORKS, tribes=TRIBES, sources=SOURCES, services=services,
	   selected_network=selected_network, selected_tribe=selected_tribe,
	   selected_source=selected_source, selected_service=selected_service)

# ----------------- Members List -----------------
@app.route("/members", methods=["GET", "POST"])
def members():
	if "logged_in" not in session:
		return redirect(url_for("login"))

	df = load_members()
	df["Network"] = df["Network"].astype(str)
	df["Tribe/Clan"] = df["Tribe/Clan"].astype(str)
	df["Source of Membership"] = df["Source of Membership"].astype(str)

	selected_network = request.form.get("Network", "All")
	selected_tribe = request.form.get("TribeClan", "All")
	selected_source = request.form.get("Source", "All")

	filtered_df = df.copy()
	if selected_network != "All":
		filtered_df = filtered_df[filtered_df["Network"].str.lower() == selected_network.lower()]
	if selected_tribe != "All":
		filtered_df = filtered_df[filtered_df["Tribe/Clan"].str.lower() == selected_tribe.lower()]
	if selected_source != "All":
		filtered_df = filtered_df[filtered_df["Source of Membership"].str.lower() == selected_source.lower()]

	# Calculate totals
	total_members = len(filtered_df)
	cat1_sources = ["WSAM-LGAM", "WSAM", "LGAM"]
	cat2_sources = ["WSAM-LGAM", "WSAM"]
	cat1_total = filtered_df[filtered_df["Source of Membership"].isin(cat1_sources)]["Name"].count()
	cat2_total = filtered_df[filtered_df["Source of Membership"].isin(cat2_sources)]["Name"].count()

	return render_template_string("""
	<!DOCTYPE html>
	<html lang="en">
	<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<title>List of Membership</title>
	<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
	<style>
		body {  
				background-image: url('{{ url_for("static", filename="background.png") }}');
				background-size: cover;
				background-position: center;
				background-repeat: no-repeat;
				background-attachment: fixed;
				font-family:"Georgia","Times New Roman", serif;
				color:#fff;
			}
			body::before {	
				content: ""; position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
				background-color: rgba(0,0,0,0.4);
				z-index: -1;
			}
		.container-card { max-width:1200px; margin:40px auto; padding:20px; background:#fff; border-radius:12px; box-shadow:0 6px 20px rgba(0,0,0,0.1); color:#000; }
		h2 { text-align:center; margin-bottom:20px; font-weight:bold; }
		table { margin-top:20px; }
		.btn-group { margin-bottom:15px; flex-wrap: wrap; }
		select, button { height:45px; }
	</style>
	</head>
	<body>
	<div class="container-card">
		<h2>📋 List of Membership</h2>

		<p><b>Total Members:</b> {{ total_members }}</p>
		<p><b>CAT 1 (WSAM-LGAM, WSAM, LGAM):</b> {{ cat1_total }}</p>
		<p><b>CAT 2 (WSAM-LGAM, WSAM):</b> {{ cat2_total }}</p>

		<form method="POST" class="btn-group d-flex">
			<select name="Network" class="form-select m-1">
				<option value="All">All Networks</option>
				{% for n in networks %}
				<option value="{{ n }}" {% if n.lower() == selected_network.lower() %}selected{% endif %}>{{ n }}</option>
				{% endfor %}
			</select>
			<select name="TribeClan" class="form-select m-1">
				<option value="All">All Tribes</option>
				{% for t in tribes %}
				<option value="{{ t }}" {% if t.lower() == selected_tribe.lower() %}selected{% endif %}>{{ t }}</option>
				{% endfor %}
			</select>
			<select name="Source" class="form-select m-1">
				<option value="All">All Sources</option>
				{% for s in sources %}
				<option value="{{ s }}" {% if s.lower() == selected_source.lower() %}selected{% endif %}>{{ s }}</option>
				{% endfor %}
			</select>
			<button type="submit" class="btn btn-primary m-1">🔍 Filter</button>
			<a href="/members" class="btn btn-secondary m-1">❌ Clear</a>
		</form>

		<div class="mt-3">
			<a href="/add_member" class="btn btn-success m-1">➕ Add Member</a>
			<a href="/edit_members_all" class="btn btn-warning m-1">✏️ Edit/Update Information</a>
			<a href="/home" class="btn btn-outline-secondary m-1">⬅ Home</a>
		</div>

		<div class="table-responsive">
			<table class="table table-striped table-bordered">
				<thead>
					<tr>
						<th>Name</th>
						<th>Network</th>
						<th>Tribe/Clan</th>
						<th>Leader</th>
						<th>Source</th>
						<th>Action</th>
					</tr>
				</thead>
				<tbody>
					{% for i, row in df.iterrows() %}
					<tr>
						<td>{{ row['Name'] }}</td>
						<td>{{ row['Network'] }}</td>
						<td>{{ row['Tribe/Clan'] }}</td>
						<td>{{ row['Tribe/Lifegroup Leader'] }}</td>
						<td>{{ row['Source of Membership'] }}</td>
						<td>
							<a href="{{ url_for('delete_member', member_id=i) }}" class="btn btn-danger btn-sm" onclick="return confirm('Are you sure?');">Delete</a>
						</td>
					</tr>
					{% endfor %}
				</tbody>
			</table>
		</div>
	</div>
	</body>
	</html>
	""", df=filtered_df, total_members=total_members, cat1_total=cat1_total, cat2_total=cat2_total,
	   networks=NETWORKS, tribes=TRIBES, sources=SOURCES,
	   selected_network=selected_network, selected_tribe=selected_tribe, selected_source=selected_source)

# ----------------- Delete Member -----------------
@app.route("/delete_member/<int:member_id>")
def delete_member(member_id):
	if "logged_in" not in session:
		return redirect(url_for("login"))

	df = load_members()
	if 0 <= member_id < len(df):
		df = df.drop(index=member_id).reset_index(drop=True)
		save_members(df)
	return redirect(url_for("members"))


# ----------------- Edit All Members -----------------
@app.route("/edit_members_all")
def edit_members_all():
	if "logged_in" not in session:
		return redirect(url_for("login"))

	df = load_members()
	return render_template_string("""
	<!DOCTYPE html>
	<html lang="en">
	<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<title>Edit Members</title>
	<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
	<style>
		body { 
				background-image: url('{{ url_for("static", filename="background.png") }}');
				background-size: cover;
				background-position: center;
				background-repeat: no-repeat;
				background-attachment: fixed;
				font-family:"Georgia","Times New Roman", serif;
				color:#fff;
			}
			body::before {	
				content: ""; position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
				background-color: rgba(0,0,0,0.4);
				z-index: -1;
			}
		.container-card { max-width:1200px; margin:40px auto; padding:20px; background:#fff; border-radius:12px; box-shadow:0 6px 20px rgba(0,0,0,0.1); color:#000; }
		h2 { text-align:center; margin-bottom:20px; font-weight:bold; }
		input { width:100%; padding:5px; font-family:inherit; }
		table { width:100%; margin-top:20px; }
		.btn-group { margin-top:15px; }
		#searchInput { width:250px; padding:5px; margin-bottom:10px; display:block; }
	</style>
	</head>
	<body>
	<div class="container-card">
		<h2>✏️ Edit/Update Information</h2>
		<a href="/home" class="btn btn-outline-secondary m-1">⬅ Back to Home</a>
		<a href="/members" class="btn btn-outline-secondary m-1">📋 List of Membership</a>
		<input type="text" id="searchInput" onkeyup="filterTable()" placeholder="Search for members...">

		<form method="POST" action="{{ url_for('update_all_members') }}">
			<div class="table-responsive">
				<table id="editTable" class="table table-striped table-bordered">
					<thead>
						<tr>
							<th onclick="sortTable(0)">Name ⬍</th>
							<th onclick="sortTable(1)">Network ⬍</th>
							<th onclick="sortTable(2)">Tribe/Clan ⬍</th>
							<th onclick="sortTable(3)">Leader ⬍</th>
							<th onclick="sortTable(4)">Source ⬍</th>
						</tr>
					</thead>
					<tbody>
						{% for i, row in df.iterrows() %}
						<tr>
							<td><input type="text" name="Name_{{i}}" value="{{ row['Name'] }}"></td>
							<td><input type="text" name="Network_{{i}}" value="{{ row['Network'] }}"></td>
							<td><input type="text" name="TribeClan_{{i}}" value="{{ row['Tribe/Clan'] }}"></td>
							<td><input type="text" name="Leader_{{i}}" value="{{ row['Tribe/Lifegroup Leader'] }}"></td>
							<td><input type="text" name="Source_{{i}}" value="{{ row['Source of Membership'] }}"></td>
						</tr>
						{% endfor %}
					</tbody>
				</table>
			</div>
			<button type="submit" class="btn btn-primary mt-2 w-100">💾 Save All Changes</button>
		</form>
	</div>

	<script>
	function sortTable(colIndex) {
		var table = document.getElementById("editTable");
		var rows = Array.from(table.tBodies[0].rows);
		var isAsc = table.getAttribute("data-sort-dir") === "asc";
		rows.sort(function(a,b){
			var x = a.cells[colIndex].querySelector("input").value.toLowerCase();
			var y = b.cells[colIndex].querySelector("input").value.toLowerCase();
			return isAsc ? x.localeCompare(y) : y.localeCompare(x);
		});
		table.setAttribute("data-sort-dir", isAsc ? "desc" : "asc");
		rows.forEach(row => table.tBodies[0].appendChild(row));
	}

	function filterTable() {
		var filter = document.getElementById("searchInput").value.toLowerCase();
		var rows = document.getElementById("editTable").tBodies[0].rows;
		for (var i=0;i<rows.length;i++) {
			var match=false;
			for(var j=0;j<rows[i].cells.length;j++){
				var input=rows[i].cells[j].querySelector("input");
				if(input && input.value.toLowerCase().includes(filter)){
					input.style.backgroundColor="yellow";
					match=true;
				} else if(input){
					input.style.backgroundColor="";
				}
			}
			rows[i].style.display=match || filter=="" ? "" : "none";
		}
	}
	</script>
	</body>
	</html>
	""", df=df)


# ----------------- Update All Members -----------------
@app.route("/update_all_members", methods=["POST"])
def update_all_members():
	if "logged_in" not in session:
		return redirect(url_for("login"))

	df = load_members()
	for i in range(len(df)):
		df.loc[i, "Name"] = request.form.get(f"Name_{i}")
		df.loc[i, "Network"] = request.form.get(f"Network_{i}")
		df.loc[i, "Tribe/Clan"] = request.form.get(f"TribeClan_{i}")
		df.loc[i, "Tribe/Lifegroup Leader"] = request.form.get(f"Leader_{i}")
		df.loc[i, "Source of Membership"] = request.form.get(f"Source_{i}")
	save_members(df)
	return redirect(url_for("members"))


# ----------------- Add Member -----------------
@app.route("/add_member", methods=["GET", "POST"])
def add_member():
	if "logged_in" not in session:
		return redirect(url_for("login"))

	if request.method == "POST":
		df = load_members()
		new_member = {
			"Name": request.form["Name"],
			"Network": request.form["Network"],
			"Tribe/Clan": request.form["TribeClan"],
			"Tribe/Lifegroup Leader": request.form["Leader"],
			"Source of Membership": request.form["Source"]
		}
		df = pd.concat([df, pd.DataFrame([new_member])], ignore_index=True)
		save_members(df)
		return redirect(url_for("members"))

	return render_template_string("""
	<!DOCTYPE html>
	<html lang="en">
	<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<title>Add New Member</title>
	<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
	<style>
		body {  
				background-image: url('{{ url_for("static", filename="background.png") }}');
				background-size: cover;
				background-position: center;
				background-repeat: no-repeat;
				background-attachment: fixed;
				font-family:"Georgia","Times New Roman", serif;
				color:#fff;
			}
			body::before {	
				content: ""; position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
				background-color: rgba(0,0,0,0.4);
				z-index: -1;
			}
		.container-card { max-width:500px; margin:60px auto; padding:30px; background:#fff; border-radius:12px; box-shadow:0 6px 20px rgba(0,0,0,0.1); color:#000; }
		h2 { text-align:center; margin-bottom:25px; font-weight:bold; }
		label { font-weight:bold; }
		input, select { width:100%; margin-bottom:15px; height:45px; padding:5px; font-family:inherit; }
		button { width:100%; padding:10px; font-weight:bold; font-family:inherit; }
		.links a { margin:5px; display:inline-block; }
	</style>
	</head>
	<body>
	<div class="container-card">
		<h2>➕ Add New Member</h2>
		<form method="POST" autocomplete="off">
			<label>Name:</label>
			<input type="text" name="Name" autocomplete="off" required>
			<label>Network:</label>
			<select name="Network" required>
				<option value="" selected disabled>-- Select Network --</option>
				{% for n in networks %}<option value="{{ n }}">{{ n }}</option>{% endfor %}
			</select>
			<label>Tribe/Clan:</label>
			<select name="TribeClan">
				<option value="" selected disabled>-- Select TribeClan --</option>
				{% for t in tribes %}<option value="{{ t }}">{{ t }}</option>{% endfor %}
			</select>
			<label>Leader:</label>
			<select name="Leader">
				<option value="" selected disabled>-- Select Leader --</option>
				{% for l in leaders %}<option value="{{ l }}">{{ l }}</option>{% endfor %}
			</select>
			<label>Source of Membership:</label>
			<select name="Source">
				<option value="" selected disabled>-- Select Source --</option>
				{% for s in sources %}<option value="{{ s }}">{{ s }}</option>{% endfor %}
			</select>
			<button type="submit" class="btn btn-primary mt-2">✅ Add Member</button>
		</form>
		<div class="links mt-3">
			<a href="/members" class="btn btn-outline-secondary">📋 List of Membership</a>
			<a href="/home" class="btn btn-outline-secondary">⬅ Home</a>
		</div>
	</div>
	</body>
	</html>
	""", networks=NETWORKS, tribes=TRIBES, leaders=LEADERS, sources=SOURCES)

# ----------------- Run Server -----------------
if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5000, debug=True)

