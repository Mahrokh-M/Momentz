# Momentz

Momentz is a Django-based web application for capturing and sharing favorite moments through photos and text. Connect with others through following, liking posts, and real-time chat, all within a vibrant neon-themed interface featuring a dynamic mouse-following particle background.

## Table of Contents
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Try It Yourself](#try-it-yourself)
- [Screenshots](#screenshots)
- [Contributing](#contributing)


## Features
- **Share Moments**: Upload photos and text to share your experiences.
- **Social Engagement**: Follow users, like posts, and chat in real-time.
- **Dynamic Homepage**: Interact with a neon-styled homepage featuring a particle background that follows your mouse cursor, enhanced with glitch animations.
- **Neon Aesthetic**: Retro-futuristic design with Tailwind CSS and custom JavaScript animations.


## Requirements
- Python 3.8+
- Django 4.x
- Microsoft SQL Server (e.g., SQL Server Express)
- ODBC Driver 17 for SQL Server
- pip
- A modern browser (Chrome, Firefox, Safari)


## Installation
1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/momentz.git
   ```
2. **Navigate to the project directory**:
   ```bash
   cd momentz
   ```
3. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   Ensure `requirements.txt` includes `django` and `pyodbc` (e.g., `pip install django pyodbc`).
5. **Set up SQL Server**:
   - Install [Microsoft SQL Server](https://www.microsoft.com/en-us/sql-server/sql-server-downloads) (e.g., Express edition).
   - Install [ODBC Driver 17 for SQL Server](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server).
   - Open SQL Server Management Studio (SSMS).
   - Create a database named `momentz_db`:
     ```sql
     CREATE DATABASE momentz_db;
     ```
   - Update the database configuration in `settings.py`:
     ```python
     DATABASES = {
         "default": {
             "ENGINE": "mssql",
             "NAME": "momentz_db",
             "USER": "your_sql_server_username",
             "PASSWORD": "your_sql_server_password",
             "HOST": r"localhost\SQLEXPRESS",
             "OPTIONS": {
                 "driver": "ODBC Driver 17 for SQL Server",
             },
         }
     }
     ```
     Replace `your_sql_server_username` and `your_sql_server_password` with your SQL Server credentials. You can also leave them empty if you're using window's authentication for ssms connection.
6. **Apply migrations**:
   ```bash
   python manage.py migrate
   ```
7. **Start the development server**:
   ```bash
   python manage.py runserver
   ```
8. Visit `http://localhost:8000` to see the app.


## Try It Yourself
To experience the Momentz homepage with its dynamic particle background:
**Run Locally**: Follow the [Installation](#installation) steps to start the Django server and visit `http://localhost:8000` in your browser. Log in or register, then upload photos or text posts. Follow users, like posts, or chat from the dashboard.
**View the Template**: Inspect the [index.html](https://github.com/Mahrokh-M/Momentz/blob/3c0071900d529deeae6b660944097a7d9d6765ed/templates/users/index.html) file in the repository to review the homepage code with a dynamic mouse-following particle background.

## Screenshots
  Below is a demo GIF iterating through Momentz’s key features, followed by static screenshots for reference:

- **Homepage**:  
  ![Homepage Screenshot](screenshots/homepage.gif)

- **App Demo**:  
  ![Momentz Demo](screenshots/momentz-demo.gif)

- **Login**:  
  ![Login Screenshot](screenshots/homepage.png)
  
- **Register**:  
  ![Register Screenshot](screenshots/register.png)

- **User Dashboard**:  
  ![Dashboard Screenshot](screenshots/dashboard1.png)
  
  ![Dashboard Screenshot](screenshots/dashboard2.png)
  
  ![Dashboard Screenshot](screenshots/dashboard3.png)
  
  ![Dashboard Screenshot](screenshots/dashboard4.png)
  
  ![Dashboard Screenshot](screenshots/dashboard5.png)

- **Chat Interface**:  
  ![Chat Screenshot](screenshots/chat.png)


  

## Contributing
We welcome contributions! To get started:
1. Fork the repository.
2. Create a branch: `git checkout -b feature/your-feature-name`.
3. Commit changes: `git commit -m "Add your feature"`.
4. Push to your branch: `git push origin feature/your-feature-name`.
5. Submit a pull request.

