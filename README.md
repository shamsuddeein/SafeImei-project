SafeIMEI - National IMEI Verification Portal
1. Project Introduction

SafeIMEI is a Django-based web application designed to combat mobile phone theft in Nigeria by providing a centralized, national database for reporting and verifying stolen devices. The platform serves two primary user groups: the general public and authorized police officers.

This project was developed as a submission for the 3MTT Cohort 3 Resilience Through Innovation Hackathon. It directly addresses the thematic areas of Economic & Financial Inclusion and Technology for Resilience by creating a safer second-hand mobile market and providing a robust tool to disrupt the cycle of theft.
Problem Statement

Every year, countless Nigerians lose their mobile phones to theft, leading to financial loss and a sense of insecurity. These stolen devices are often resold to unsuspecting buyers, perpetuating a criminal cycle. SafeIMEI tackles this problem by making it easy for the public to verify a device's status before purchase and by empowering law enforcement to track stolen phones effectively.
2. Key Features
For the Public

    Instant IMEI Check: A simple, free-to-use form on the homepage to check if a phone's IMEI has been reported as stolen.

    Real-time Validation: The IMEI input field provides live feedback on the format and validity of the entered number.

    Informational Pages: Comprehensive "About Us", "FAQ", and "Privacy Policy" pages to build user trust and explain the platform's mission and operation.

For Police Officers

    Secure Officer Portal: A protected, login-required portal for law enforcement personnel.

    Two-Factor Authentication (2FA): Secure login process that sends a 6-digit code to the officer's registered email, ensuring only authorized access.

    Live Data Dashboard: A dashboard displaying real-time statistics, including reports filed this month, reports pending review, and recently recovered devices for the officer's station.

    Multi-Step Report Creation: An intuitive, multi-step form to file detailed reports for stolen devices, collecting owner, device, and incident information, along with proofs of ownership.

    View and Search Reports: A comprehensive table of all reports filed by the officer's station, with the ability to search by IMEI.

3. Tech Stack

    Backend: Django

    Database: SQLite3 (for development)

    Frontend: HTML, Tailwind CSS, JavaScript

    Environment Management: Pipenv

4. Prerequisites

Before you begin, ensure you have the following installed on your local machine:

    Python 3.12+

    Pipenv

5. Local Setup and Installation

Follow these steps to get the project running on your local machine.
Step 1: Clone the Repository

First, clone the project repository to your local machine.

git clone https://github.com/shamsuddeein/SafeImei-project.git
cd SafeImei-project/backend

Step 2: Install Dependencies with Pipenv

This project uses Pipenv to manage dependencies. The Pipfile contains all the necessary packages. Run the following command to install them:

pipenv install

This command will create a new virtual environment for the project and install Django and its dependencies.
Step 3: Activate the Virtual Environment

To use the installed packages, you need to activate the pipenv shell:

pipenv shell

Your command prompt should now be prefixed with the name of the virtual environment (e.g., (backend)).
Step 4: Apply Database Migrations

The project uses a SQLite database, which is included in the repository for convenience. Run the migrate command to ensure the database schema is up to date with the models:

python manage.py migrate

6. Create Superuser and Initial Data

To access the Django admin and the officer portal, you need to create user accounts.
Step 1: Create a Superuser

The superuser has full access to the Django admin interface.

python manage.py createsuperuser

Follow the prompts to create your superuser account.
Step 2: Set Up Stations and Officer Profiles (via Admin)

    Run the development server (see next section).

    Navigate to http://127.0.0.1:8000/admin/.

    Log in with your superuser credentials.

    Create a Station:

        Go to the "Stations" section and click "Add Station".

        Create at least one station (e.g., Name: Kaduna Division, Location: Kaduna).

    Create an Officer User:

        Go to the "Users" section and click "Add User".

        Create a new user. Make sure to provide a valid email address, as this will be used for 2FA. Set a password.

    Create an Officer Profile:

        Go to the "Officer Profiles" section and click "Add Officer Profile".

        Link the user you just created to the station you created.

7. Running the Application

Once the setup is complete, you can run the local development server from the backend directory:

python manage.py runserver

The application will be available at http://127.0.0.1:8000/.

    Public Portal: http://127.0.0.1:8000/

    Officer Login: http://127.0.0.1:8000/login/

    Django Admin: http://127.0.0.1:8000/admin/

8. Deployment Notes

To deploy this application to a production server, the following changes are critical:

    SECRET_KEY: The SECRET_KEY in safeimei_project/settings.py must be replaced with a secure key loaded from an environment variable.

    DEBUG Mode: DEBUG must be set to False in settings.py for production.

    ALLOWED_HOSTS: The domain name of your live site must be added to ALLOWED_HOSTS in settings.py.

    Database: Switch from SQLite3 to a more robust database like PostgreSQL for production.

    Static Files: Run python manage.py collectstatic and configure a web server (like Nginx) to serve the static files.

    Email Backend: Configure a production-ready EMAIL_BACKEND in settings.py (e.g., using SendGrid, Mailgun) to send real 2FA emails.