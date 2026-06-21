import os
import json
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "super_secret_pet_key_123" # Required for managing user sessions

PETS_DB = "pets_db.json"
USERS_DB = "users_db.json"

# Initialize databases with rich dummy data if they don't exist
if not os.path.exists(PETS_DB):
    initial_pets = [
        {"id": 1, "name": "Max", "species": "Dog", "breed": "Golden Retriever", "age": 2, "status": "Available", "image": "https://images.unsplash.com/photo-1552053831-71594a27632d?w=500", "weight": "28kg", "vaccines": "Up to date", "next_vet": "2026-08-12", "notes": "Enjoys outdoor frisbee."},
        {"id": 2, "name": "Luna", "species": "Cat", "breed": "Siamese", "age": 1, "status": "Available", "image": "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=500", "weight": "4kg", "vaccines": "Pending Booster", "next_vet": "2026-07-01", "notes": "Calm, loves window basking."},
        {"id": 3, "name": "Bella", "species": "Dog", "breed": "French Bulldog", "age": 3, "status": "Available", "image": "https://images.unsplash.com/photo-1583511655857-d19b40a7a54e?w=500", "weight": "11kg", "vaccines": "Up to date", "next_vet": "2026-09-20", "notes": "Sensitive skin. Needs special diet grain-free food."}
    ]
    with open(PETS_DB, "w") as f: json.dump(initial_pets, f, indent=4)

if not os.path.exists(USERS_DB):
    with open(USERS_DB, "w") as f: json.dump([], f)

def read_json(filename):
    with open(filename, "r") as f: return json.load(f)

def write_json(filename, data):
    with open(filename, "w") as f: json.dump(data, f, indent=4)

# --- WEB PAGE ROUTING ---
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/auth")
def auth_page():
    return render_template("auth.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("auth_page"))
    return render_template("dashboard.html", username=session["user"])

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))

# --- BACKEND API ENDPOINTS ---
@app.post("/api/register")
def register():
    data = request.json
    users = read_json(USERS_DB)
    if any(u["username"] == data["username"] for u in users):
        return jsonify({"error": "User already exists"}), 400
    users.append({"username": data["username"], "password": data["password"]}) # Plain text for simplicity
    write_json(USERS_DB, users)
    return jsonify({"success": True})

@app.post("/api/login")
def login():
    data = request.json
    users = read_json(USERS_DB)
    for u in users:
        if u["username"] == data["username"] and u["password"] == data["password"]:
            session["user"] = u["username"]
            return jsonify({"success": True})
    return jsonify({"error": "Invalid credentials"}), 401

@app.get("/api/pets")
def get_pets():
    return jsonify(read_json(PETS_DB))

@app.post("/api/pets")
def add_pet():
    data = request.json
    pets = read_json(PETS_DB)
    new_pet = {
        "id": len(pets) + 1,
        "name": data["name"],
        "species": data["species"],
        "breed": data["breed"],
        "age": int(data["age"]),
        "status": "Available",
        "image": data.get("image") or "https://images.unsplash.com/photo-1543466835-00a7907e9de1?w=500",
        "weight": data.get("weight", "Unknown"),
        "vaccines": data.get("vaccines", "Unknown"),
        "next_vet": data.get("next_vet", "None Scheduled"),
        "notes": data.get("notes", "No notes.")
    }
    pets.append(new_pet)
    write_json(PETS_DB, pets)
    return jsonify(new_pet)

@app.patch("/api/pets/<int:pet_id>/adopt")
def adopt_pet(pet_id):
    pets = read_json(PETS_DB)
    for p in pets:
        if p["id"] == pet_id:
            p["status"] = f"Adopted by {session.get('user', 'Anonymous')}"
            write_json(PETS_DB, pets)
            return jsonify(p)
    return jsonify({"error": "Pet not found"}), 404

@app.patch("/api/pets/<int:pet_id>/health")
def update_health(pet_id):
    data = request.json
    pets = read_json(PETS_DB)
    for p in pets:
        if p["id"] == pet_id:
            p["weight"] = data.get("weight", p["weight"])
            p["vaccines"] = data.get("vaccines", p["vaccines"])
            p["next_vet"] = data.get("next_vet", p["next_vet"])
            p["notes"] = data.get("notes", p["notes"])
            write_json(PETS_DB, pets)
            return jsonify(p)
    return jsonify({"error": "Pet not found"}), 404

if __name__ == "__main__":
    app.run(debug=True, port=5000)