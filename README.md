# Child-Safe Search Engine

## Overview
This project is a child-safe search engine designed to offer a secure browsing experience for children. It leverages Google’s Custom Search API to allow children to explore the internet safely under their parents' supervision. The application is built with Django, ensuring a robust, scalable, and secure platform.

## Features
- **Safe Search Filtering**: Utilizes Google's Custom Search API to filter out inappropriate content, ensuring that search results are suitable for children.
- **Parental Controls**: Parents can monitor and control their child's search activities, providing a safe online environment.
- **Real-Time Alerts**: Sends immediate notifications to parents for any unauthorized search attempts or activities.
- **Activity Logging**: Keeps a log of all search activities, allowing parents to review their child's online behavior.
- **Request Unban**: Children can request their parents to unban certain words, promoting a learning opportunity and open communication.
- **Report Inappropriate Content**: Children can report any inappropriate content, helping to improve the search engine's safety measures.
- **Customizable Settings**: Parents can customize the search engine settings to suit their child's needs, They can set alert levels and access times as well as take advantage of our custom list of banned words with each child having a diiferent list of banned words thay can't search.
- **Discussion Forum**: Parents can discuss and share experiences with other parents, fostering a supportive community.
- **Educational Resources**: Provides access to educational resources and materials, enhancing the child's learning experience and teaching all users about staying safe online.

## Technology Stack
- **Backend Framework**: Django
- **Frontend Technologies**: HTML, CSS, JavaScript (For admin and parental control interfaces)
- **APIs**: Google Custom Search API
- **Database**: SQLite (for development), PostgreSQL (for production)

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Python 3.6+
- A Google Custom Search API Key
- A Google API Key

### Installation

1. Clone the repository to your local machine:
```bash
git clone https://github.com/nafdev01/childprotect.git
```

2. Navigate to the project directory:
```bash
cd childprotect
```
3. Create a virtual environment:
```bash
python3 -m venv .venv
```
4. Activate the virtual environment:
```bash
source .venv/bin/activate
```

5. Install the project dependencies:
```bash
pip install -r requirements.txt
```

6. Create a `.env` file in the project root directory using the .env.example as a template:

7. Run the Django migrations:
```bash
python manage.py migrate
```

8. Create an admin user:
```bash
python manage.py createsuperuser
```

9. Start the Django development server:
```bash
python manage.py runserver
```

10. Access the application at `http://localhost:8000/` and the admin interface at `http://localhost:8000/admin/`.

### NOTE
 - If you set development mode to false you will need to set up a postgresql database for yourapplication. For simplicity and local deployment use the default sqlite database. 
 - Instructions on how to set up postgresql with django can be found at https://www.digitalocean.com/community/tutorials/how-to-use-postgresql-with-your-django-application-on-ubuntu-20-04

 ## Troubleshooting
 - If you encounter any issues while setting up the project, please feel free to open an issue on the repository.
 - If you encounter a database error while running the project, please ensure that you have run the migrations using the `python manage.py migrate` command and are using the correct postgresql database configuration.

 ## Contribution Guidelines
 - If you would like to contribute to the project, please fork the repository and submit a pull request.

## Acknowledgments

- Google Custom Search API
- Django Community
- All contributors and supporters of this project


