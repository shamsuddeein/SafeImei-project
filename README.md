# SafeIMEI: National Stolen Phone Reporting Database

**Live Demo:** [https://safeimei.onrender.com/](https://safeimei.onrender.com/)

SafeIMEI is a tech enabled platform that builds societal resilience by directly disrupting the market for stolen mobile phones in Nigeria. It provides a centralized, official database for law enforcement to report stolen devices and a free, instant verification tool for the public to check a phone's status before buying.

---

## 📑 Table of Contents
- [The Problem](#-the-problem)
- [Our Solution](#-our-solution)
- [Key Features](#%EF%B8%8F-key-features)
- [Tech Stack](#-tech-stack)
- [Getting Started (Local Setup)](#%EF%B8%8F-getting-started-local-setup)
- [Usage](#-usage)
- [The Team](#%EF%B8%8F-the-team)
- [License](#-license)

---

## ❗ The Problem
Phone theft is a pervasive issue in Nigeria. The thriving second-hand market allows stolen devices to be easily resold to unsuspecting buyers, fueling a cycle of crime.

There is no centralized, reliable way for buyers to verify if a device has been reported stolen, putting them at financial and legal risk.

---

## 💡 Our Solution
SafeIMEI tackles this problem with a two-pronged approach:

### A Secure Law Enforcement Portal
A private, secure dashboard for authorized police officers to file, manage, and track official reports of stolen devices using their unique IMEI numbers.

### A Free Public IMEI Verification Tool
A simple, public-facing website that allows anyone to instantly check an IMEI against the national database to see if it has been flagged as stolen.

> This approach de-incentivizes theft by making it much harder to sell stolen goods.

---

## ⚙️ Key Features

### Public-Facing Site
- **Instant IMEI Check:** Check the status of any 15-digit IMEI number for free.
- **Luhn Algorithm Validation:** Real-time validation on the input field to ensure the IMEI format is correct.
- **Anonymous Alert:** If a checked IMEI is stolen, the user can anonymously send their approximate location to the reporting police station to aid investigation.
- **Informational Pages:** About, FAQ, Contact, and Privacy Policy pages.

### Officer Portal
- **Secure Authentication:** Station ID and password login.
- **Two-Factor Authentication (2FA):** A 6-digit code is sent to the officer's registered email for verification.
- **Officer Dashboard:** A summary of station activity, including monthly reports and pending reviews.
- **Multi-Step Report Creation:** An intuitive, multi-page form to guide officers through filing a new report.
- **View & Search Reports:** A comprehensive list of all reports filed by the officer's station, with search functionality.

---

## 🧠 Tech Stack
- **Backend:** Python, Django
- **Frontend:** HTML, Tailwind CSS, Vanilla JavaScript
- **Database:** PostgreSQL (Production), SQLite (Development)
- **Deployment:** Render (via Gunicorn & Whitenoise)
- **DevOps:** Pipenv for dependency management.

---

## 🛠️ Getting Started (Local Setup)

Follow these instructions to get the project running on your local machine.

### Prerequisites
- Python 3.12+
- Pipenv (`pip install pipenv`)
- PostgreSQL installed and running *(optional, can use default SQLite)*

### Setup Instructions

**Clone the repository:**
```bash
git clone https://github.com/shamsuddeein/SafeImei-project.git
cd SafeImei-project/backend
```

**Install dependencies:**
```bash
pipenv install
pipenv shell
```

**Set up environment variables:**
- Create a file named `.env` in the `backend/` directory.
- Copy the contents of `.env.production` into it and modify the values for your local setup.

**For local SQLite (easier setup):**
- Comment out all the `DATABASE_*` variables and Django will default to `db.sqlite3`.

**For local PostgreSQL:**
```
SECRET_KEY=your-super-secret-key-here
DEBUG=True
ALLOWED_HOSTS=.localhost,127.0.0.1

# Your local PostgreSQL details
DATABASE_NAME=safeimei_db
DATABASE_USER=your_postgres_user
DATABASE_PASSWORD=your_postgres_password
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Email settings for 2FA (can use console backend for dev)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
# EMAIL_HOST=smtp.gmail.com
# ... etc
```

**Run database migrations:**
```bash
python manage.py migrate
```

**Create a superuser for admin access:**
```bash
python manage.py createsuperuser
```

**Seed the database with demo data:**
> This command creates stations for all Nigerian states, two officer accounts per station, and 100 sample device reports.
```bash
python manage.py seed_data
```

**Run the development server:**
```bash
python manage.py runserver
```

> The application will be available at [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 🚀 Usage
- **Public Site:** Navigate to [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Admin Panel:** Access the Django admin at [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) with your superuser credentials.
- **Officer Portal:**
  - Navigate to [http://127.0.0.1:8000/login/](http://127.0.0.1:8000/login/)
  - Use one of the seeded demo accounts to log in.
  - **Username:** `LAG01` *(or `FCT01`, `KAN02`, etc.)*
  - **Password:** `password123`
  - The 2FA code will be printed in your terminal/console since we configured the console email backend.

---

## 🧑‍💻 The Team
This project was built for the **3MTT Cohort 3 Hackathon** by **Team SafeImei**:

- **SHAMSUDDEEN YUSUF** — Team Lead, Founder & Backend Developer
- **FRIDAY AKASHIE EUGENE** — Project Manager
- **SA’ADIYA ABDULLAHI** — Frontend Developer

---

## 📜 License
This project is licensed under the **MIT License**. See the `LICENSE` file for details.
