IPCO Internal News & Corporate Information Portal

<p align="center">
  <strong>A Django-based internal corporate portal for centralized news, announcements, meetings, training, and organizational information.</strong>
</p>
<p align="center">
  <img src="https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/Django-5.2-092E20?style=for-the-badge&logo=django&logoColor=white">
  <img src="https://img.shields.io/badge/PostgreSQL-17-4169E1?style=for-the-badge&logo=postgresql&logoColor=white">
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white">
</p>

📌 Overview

IPCO Internal News & Corporate Information Portal is a modular web application built with Python and Django to centralize internal communication and organizational information.

The project was developed as part of a Software Engineering internship at Iran Khodro Powertrain Company (IPCO) within the IT Department.

The platform provides a unified environment for:

* 📰 Corporate news
* 📢 Internal announcements
* 📅 Meetings and room reservations
* 📧 Meeting email notifications
* 👥 Organizational workgroups
* 🎓 Training content
* 🏢 Corporate information pages
* ⚙️ Administrative content management

✨ Core Features

News & Announcements

* Create, edit, delete, and publish content
* News and announcement listing/detail pages
* Featured images and pagination
* Django Admin management

Meetings

* Meeting creation and management
* Meeting-room reservation
* Participant selection
* Email invitations
* Meeting cancellation notifications

Workgroups

* Organizational workgroup profiles
* Member information
* Employee relationships
* Dedicated workgroup pages

Training

* Internal educational content
* Training listings and detail pages
* Administrative management

🏗️ Architecture

The project follows a modular Django architecture, separating major business domains into independent applications:

IPCO Portal
│
├── core
├── home
├── news
├── announcements
├── meetings
├── training
└── workgroups

A typical request follows the standard Django flow:

Browser
   ↓
URLConf
   ↓
View
   ↓
Form / Django ORM
   ↓
Database
   ↓
Template
   ↓
HTML Response

🛠️ Technology Stack

Technology	Purpose
Python	Backend programming
Django	Web framework
Django ORM	Database access
Django Templates	Server-side rendering
Django Forms	Form handling & validation
Django Admin	Content management
HTML5 / CSS3 / JavaScript	Frontend
SQLite	Development database
Docker / Docker Compose	Containerization
Gunicorn	WSGI application server
Git / GitHub	Version control

🎨 UI/UX

The interface was designed for a Persian corporate environment with:

* Full RTL support
* Persian typography
* Responsive layouts
* Desktop, tablet, and mobile support
* Light and Dark modes
* Consistent component design
* Accessible content hierarchy

The frontend uses Django template inheritance and reusable partials to maintain consistency across the application.

🐳 Docker

Build and run the application using Docker Compose:

docker compose build
docker compose up -d

Stop the containers:

docker compose down

💻 Local Development

git clone <repository-url>
cd <project-directory>
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver


📧 Email Workflow

Meeting notifications are integrated into the meeting lifecycle:

Create Meeting
      ↓
Select Room & Participants
      ↓
Save Meeting
      ↓
Generate Invitation
      ↓
Send Email

For cancellations:

Cancel Meeting
      ↓
Generate Cancellation Notice
      ↓
Send Email

🔐 Security

The project uses Django’s built-in security mechanisms, including:

* CSRF protection
* Password hashing
* Session management
* Form validation
* ORM-based database access
* Authentication
* Host validation

Production deployments should additionally use HTTPS, secure cookies, secret management, secure headers, and DEBUG=False.

🔮 Future Development

Potential extensions include:

* Django REST Framework API
* PostgreSQL for production
* Redis caching
* Advanced authentication and permissions
* Internal notification center
* Full-text search
* Expanded automated testing
* Mobile application

🏢 Internship Context

Field	Information
Organization	Iran Khodro Powertrain Company (IPCO)
Department	IT Department
Major	Software Engineering
Project Type	Internal Corporate Web Application
Developer	Shahab Hamidi
Company Supervisor	Mehralizadeh
Period	July 2026

👨‍💻 Developer

Shahab Hamidi

Ali Mosayebi

Software Engineering Student | Backend Developer

Focused on:

Python · Django · Django REST Framework · Backend Development · Database Design · Docker

📄 Project Status

Completed — Functional Internal Corporate Portal

This project was developed for an internal organizational environment.

⸻

<p align="center">
  <strong>IPCO Internal News & Corporate Information Portal</strong>
  <br>
  Built with Python & Django
  <br><br>
  <sub>Software Engineering Project</sub>
</p>
