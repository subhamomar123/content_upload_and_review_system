import json
import pytest
from app import app, db
from app.models import Movie


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["UPLOAD_FOLDER"] = "uploads"

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()


def test_upload_file_valid(client):
    data = {
        "file": (
            open("tests/test_movies.csv", "rb"),
            "test_movies.csv",
        )
    }
    response = client.post("/api/upload", data=data)
    assert response.status_code == 200
    assert b"File uploaded and data saved successfully" in response.data


def test_upload_file_no_file(client):
    response = client.post("/api/upload")
    assert response.status_code == 400
    assert b"No file part" in response.data


def test_upload_file_empty_filename(client):
    data = {"file": (open("tests/empty_file.csv", "rb"), "")}
    response = client.post("/api/upload", data=data)
    assert response.status_code == 400
    assert b"No file selected" in response.data


def test_upload_file_invalid_extension(client):
    data = {
        "file": (
            open("tests/test_movies.txt", "rb"),
            "test_movies.txt",
        )
    }
    response = client.post("/api/upload", data=data)
    assert response.status_code == 400
    assert b"Invalid file type, must be a CSV" in response.data


def test_upload_file_missing_columns(client):
    data = {
        "file": (
            open("tests/test_movies_missing_columns.csv", "rb"),
            "test_movies_missing_columns.csv",
        )
    }
    response = client.post("/api/upload", data=data)
    assert response.status_code == 400
    assert b"Missing columns: language" in response.data


# Test cases for the /api/movies endpoint
def test_get_movies_empty(client):
    response = client.get("/api/movies?page=1")
    assert response.status_code == 200
    assert json.loads(response.data) == {
        "movies": [],
        "total": 0,
        "page": 1,
        "per_page": 10,
    }


def test_get_movies(client):
    data = {
        "file": (
            open("tests/test_movies.csv", "rb"),
            "test_movies.csv",
        )
    }
    client.post("/api/upload", data=data)

    response = client.get("/api/movies?page=1")
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert len(response_data["movies"]) > 0
    assert "title" in response_data["movies"][0]


def test_get_movies_with_filter(client):
    data = {
        "file": (
            open("tests/test_movies.csv", "rb"),
            "test_movies.csv",
        )
    }
    client.post("/api/upload", data=data)

    response = client.get("/api/movies?page=1&language=en")
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert all(movie["original_language"] == "en" for movie in response_data["movies"])


def test_get_movies_sort_by_release_date(client):
    data = {
        "file": (
            open("tests/test_movies.csv", "rb"),
            "test_movies.csv",
        )
    }
    client.post("/api/upload", data=data)

    response = client.get("/api/movies?page=1&sort_by=release_date&sort_order=desc")
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert (
        response_data["movies"][0]["release_date"]
        >= response_data["movies"][1]["release_date"]
    )


def test_get_movies_pagination(client):
    # Upload valid data
    data = {
        "file": (
            open("tests/test_movies.csv", "rb"),
            "test_movies.csv",
        )
    }
    client.post("/api/upload", data=data)

    # Retrieve movies with pagination
    response = client.get("/api/movies?page=2&per_page=5")
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert len(response_data["movies"]) == 5  # Assuming there are more than 5 movies
    assert response_data["page"] == 2


def test_get_movies_invalid_filter(client):
    # Upload valid data
    data = {
        "file": (
            open("tests/test_movies.csv", "rb"),
            "test_movies.csv",
        )
    }
    client.post("/api/upload", data=data)

    # Try filtering with an invalid field
    response = client.get("/api/movies?page=1&language=invalid_language")
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert response_data["movies"] == []  # No movies should match the invalid filter


def test_get_movies_sort_invalid_order(client):
    # Upload valid data
    data = {
        "file": (
            open("tests/test_movies.csv", "rb"),
            "test_movies.csv",
        )
    }
    client.post("/api/upload", data=data)

    # Try sorting with an invalid sort order
    response = client.get("/api/movies?page=1&sort_by=release_date&sort_order=invalid")
    assert response.status_code == 400
    assert b"Invalid sort order" in response.data
