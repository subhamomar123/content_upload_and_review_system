# Content Upload and Review System

This project is a Content Upload and Review System built with Flask, designed to allow users to upload movie/show data through CSV files, manage the content, and view the list of available movies/shows in a paginated manner with filtering and sorting options.

## Features

- Upload CSV files containing movie/show data
- Store and manage movie/show information in a database
- Retrieve a paginated list of movies/shows
- Filter movies/shows by language
- Sort movies/shows by various attributes
- API endpoints for uploading and retrieving data

## Technologies Used

- **Backend**: Flask
- **Database**: SQLite (via SQLAlchemy)
- **Data Handling**: Pandas
- **Environment**: Python 3.x
- **Dependencies**: Flask, SQLAlchemy, Pandas, Werkzeug

## Getting Started

### Prerequisites

- Python 3.x
- Pip (Python package installer)

### Installation

1. Clone the repository:

   git clone https://github.com/subhamomar123/content_upload_and_review_system/edit/main/readme.md
   cd content_upload_and_review_system

2. Create a virtual environment:

    python -m venv venv

3. Activate the virtual environment:

   venv\Scripts\activate

4. Install the required packages:

    pip install -r requirements.txt

5. Run the Flask application:

    flask run

6. Run the tests

    pytest
