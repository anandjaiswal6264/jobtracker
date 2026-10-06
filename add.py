from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_

app = Flask(__name__)

# Database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///jobtrack.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ==============================
# JOB MODEL
# ==============================

class Job(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    company = db.Column(db.String(100), nullable=False)

    position = db.Column(db.String(100), nullable=False)

    location = db.Column(db.String(100), nullable=False)

    status = db.Column(db.String(50), nullable=False)

    applied_date = db.Column(db.String(20), nullable=False)


# Create database
with app.app_context():
    db.create_all()


# ==============================
# HOME
# ==============================

@app.route("/")
def home():

    search = request.args.get("search", "")
    status = request.args.get("status", "")

    query = Job.query

    # Search
    if search:
        query = query.filter(
            or_(
                Job.company.ilike(f"%{search}%"),
                Job.position.ilike(f"%{search}%")
            )
        )

    # Filter
    if status:
        query = query.filter(
            Job.status == status
        )

    jobs = query.all()

    # Statistics
    total = Job.query.count()

    applied = Job.query.filter_by(
        status="Applied"
    ).count()

    interview = Job.query.filter_by(
        status="Interview"
    ).count()

    selected = Job.query.filter_by(
        status="Selected"
    ).count()

    rejected = Job.query.filter_by(
        status="Rejected"
    ).count()

    return render_template(
        "index.html",
        jobs=jobs,
        total=total,
        applied=applied,
        interview=interview,
        selected=selected,
        rejected=rejected,
        search=search,
        status=status
    )


# ==============================
# ADD JOB
# ==============================

@app.route("/add", methods=["GET", "POST"])
def add_job():

    if request.method == "POST":

        company = request.form["company"]
        position = request.form["position"]
        location = request.form["location"]
        status = request.form["status"]
        applied_date = request.form["applied_date"]

        job = Job(
            company=company,
            position=position,
            location=location,
            status=status,
            applied_date=applied_date
        )

        db.session.add(job)
        db.session.commit()

        return redirect(url_for("home"))

    return render_template("add_job.html")


# ==============================
# EDIT JOB
# ==============================

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_job(id):

    job = Job.query.get_or_404(id)

    if request.method == "POST":

        job.company = request.form["company"]
        job.position = request.form["position"]
        job.location = request.form["location"]
        job.status = request.form["status"]
        job.applied_date = request.form["applied_date"]

        db.session.commit()

        return redirect(url_for("home"))

    return render_template(
        "edit_job.html",
        job=job
    )


# ==============================
# DELETE JOB
# ==============================

@app.route("/delete/<int:id>")
def delete_job(id):

    job = Job.query.get_or_404(id)

    db.session.delete(job)
    db.session.commit()

    return redirect(url_for("home"))


# ==============================
# API - GET ALL JOBS
# ==============================

@app.route("/api/jobs", methods=["GET"])
def get_jobs():

    jobs = Job.query.all()

    result = []

    for job in jobs:

        result.append({
            "id": job.id,
            "company": job.company,
            "position": job.position,
            "location": job.location,
            "status": job.status,
            "applied_date": job.applied_date
        })

    return jsonify(result)


# ==============================
# API - GET ONE JOB
# ==============================

@app.route("/api/jobs/<int:id>", methods=["GET"])
def get_one_job(id):

    job = Job.query.get_or_404(id)

    return jsonify({
        "id": job.id,
        "company": job.company,
        "position": job.position,
        "location": job.location,
        "status": job.status,
        "applied_date": job.applied_date
    })


# ==============================
# API - CREATE JOB
# ==============================

@app.route("/api/jobs", methods=["POST"])
def create_job():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "JSON data required"
        }), 400

    if "company" not in data:
        return jsonify({
            "error": "Company is required"
        }), 400

    if "position" not in data:
        return jsonify({
            "error": "Position is required"
        }), 400

    job = Job(
        company=data["company"],
        position=data["position"],
        location=data.get("location", ""),
        status=data.get("status", "Applied"),
        applied_date=data.get("applied_date", "")
    )

    db.session.add(job)
    db.session.commit()

    return jsonify({
        "message": "Job created successfully",
        "id": job.id
    }), 201


# ==============================
# API - UPDATE JOB
# ==============================

@app.route("/api/jobs/<int:id>", methods=["PUT"])
def update_job(id):

    job = Job.query.get_or_404(id)

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "JSON data required"
        }), 400

    job.company = data.get(
        "company",
        job.company
    )

    job.position = data.get(
        "position",
        job.position
    )

    job.location = data.get(
        "location",
        job.location
    )

    job.status = data.get(
        "status",
        job.status
    )

    job.applied_date = data.get(
        "applied_date",
        job.applied_date
    )

    db.session.commit()

    return jsonify({
        "message": "Job updated successfully"
    })


# ==============================
# API - DELETE JOB
# ==============================

@app.route("/api/jobs/<int:id>", methods=["DELETE"])
def delete_job_api(id):

    job = Job.query.get_or_404(id)

    db.session.delete(job)
    db.session.commit()

    return jsonify({
        "message": "Job deleted successfully"
    })


# ==============================
# RUN
# ==============================

if __name__ == "__main__":
    app.run(debug=True)