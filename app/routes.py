# app/routes.py

import os
import traceback
from flask import request, jsonify
from werkzeug.utils import secure_filename
from app import app, db
from app.models import Movie
import pandas as pd
from datetime import datetime
from sqlalchemy import desc

if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])

ALLOWED_EXTENSIONS = {"csv"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/api/upload", methods=["POST"])
def upload_file():
    # Check if file part is in request
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

        try:
            file.save(file_path)

            # Try reading CSV with UTF-8 encoding first
            try:
                df = pd.read_csv(file_path, encoding="utf-8", on_bad_lines="skip")
            except UnicodeDecodeError:
                # Fallback to ISO-8859-1 encoding if UTF-8 fails
                df = pd.read_csv(file_path, encoding="ISO-8859-1", on_bad_lines="skip")

            required_columns = [
                "title",
                "original_title",
                "overview",
                "release_date",
                "budget",
                "revenue",
                "runtime",
                "vote_average",
                "vote_count",
                "status",
                "homepage",
                "original_language",
                "production_company_id",
                "genre_id",
                "languages",
            ]

            # Check if the CSV has all required columns
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return (
                    jsonify(
                        {"error": f"Missing columns: {', '.join(missing_columns)}"}
                    ),
                    400,
                )

            for _, row in df.iterrows():
                # Process and validate release_date
                release_date_str = (
                    row["release_date"] if pd.notna(row["release_date"]) else None
                )
                release_date = None
                if release_date_str:
                    try:
                        release_date = datetime.strptime(release_date_str, "%Y-%m-%d")
                    except ValueError:
                        return (
                            jsonify(
                                {"error": f"Invalid date format for {row['title']}"}
                            ),
                            400,
                        )

                # Create Movie instance
                movie = Movie(
                    title=row["title"],
                    original_title=row["original_title"],
                    overview=row["overview"],
                    release_date=release_date,
                    budget=int(row["budget"]) if pd.notna(row["budget"]) else None,
                    revenue=int(row["revenue"]) if pd.notna(row["revenue"]) else None,
                    runtime=int(row["runtime"]) if pd.notna(row["runtime"]) else None,
                    vote_average=(
                        float(row["vote_average"])
                        if pd.notna(row["vote_average"])
                        else None
                    ),
                    vote_count=(
                        int(row["vote_count"]) if pd.notna(row["vote_count"]) else None
                    ),
                    status=row["status"],
                    homepage=row["homepage"],
                    original_language=row["original_language"],
                    production_company_id=(
                        int(row["production_company_id"])
                        if pd.notna(row["production_company_id"])
                        else None
                    ),
                    genre_id=(
                        int(row["genre_id"]) if pd.notna(row["genre_id"]) else None
                    ),
                    languages=(
                        ",".join(eval(row["languages"]))
                        if pd.notna(row["languages"])
                        else None
                    ),
                )
                db.session.add(movie)

            db.session.commit()
            return (
                jsonify({"message": "File uploaded and data saved successfully"}),
                200,
            )

        except Exception as e:
            print(traceback.format_exc())
            return (
                jsonify(
                    {
                        "error": "An error occurred during file processing",
                        "details": str(e),
                    }
                ),
                500,
            )
    else:
        return jsonify({"error": "Invalid file type, must be a CSV"}), 400


@app.route("/api/movies", methods=["GET"])
def get_movies():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    sort_by = request.args.get("sort_by", "title")
    sort_order = request.args.get("sort_order", "asc")

    if sort_order not in ["asc", "desc"]:
        return jsonify({"error": "Invalid sort order"}), 400
    filters = {}
    language = request.args.get("language")
    if language:
        filters["original_language"] = language

    query = Movie.query.filter_by(**filters)

    if sort_order == "desc":
        query = query.order_by(desc(sort_by))
    else:
        query = query.order_by(sort_by)
    
    movies = query.paginate(page=page, per_page=per_page, error_out=False)

    response = {
        "total": movies.total,
        "page": movies.page,
        "per_page": movies.per_page,
        "movies": [
            {
                "id": movie.id,
                "title": movie.title,
                "original_title": movie.original_title,
                "overview": movie.overview,
                "release_date": (
                    movie.release_date.strftime("%Y-%m-%d")
                    if movie.release_date
                    else None
                ),
                "budget": movie.budget,
                "revenue": movie.revenue,
                "runtime": movie.runtime,
                "vote_average": movie.vote_average,
                "vote_count": movie.vote_count,
                "status": movie.status,
                "homepage": movie.homepage,
                "original_language": movie.original_language,
                "production_company_id": movie.production_company_id,
                "genre_id": movie.genre_id,
                "languages": movie.languages,
            }
            for movie in movies.items
        ],
    }

    return jsonify(response), 200
