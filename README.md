![homepage](https://github.com/user-attachments/assets/371d3eda-64e3-417c-9f77-090245bb4e78)# Momentz

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
![homepage](https://github.com/user-attachments/assets/ded2da10-ae33-466e-ad0e-069cef0f7683)


- **App Demo**:  
![demo](https://github.com/user-attachments/assets/85c285e2-cbdb-4869-a920-e34226673137)


- **Login**:  
  ![login](https://github.com/user-attachments/assets/5118e634-2b67-43d6-9752-ca1e95247a3c)

- **Register**:
  ![register](https://github.com/user-attachments/assets/8dee6aeb-7edb-4d84-9097-3f21a31f335d)

- **User Dashboard**:  

  ![dashboard1](https://github.com/user-attachments/assets/c8686e0b-2ed9-4dad-b46a-5efde50e6f9c)

  ![dashboard2](https://github.com/user-attachments/assets/87a22287-3040-4162-b2fe-bde8aba71785)

  ![dashboard3](https://github.com/user-attachments/assets/43f5bb3f-ca20-4044-8991-2a7e5ed8e4c9)

  ![dashboard5](https://github.com/user-attachments/assets/cf2f2617-79e9-44cf-9e7a-c357fb934106)

  ![post](https://github.com/user-attachments/assets/327cac2f-711d-430f-a948-01de2df63297)

- **Chat Interface**:
  ![chat](https://github.com/user-attachments/assets/16ca2833-d8c0-46f4-bbef-62d637755580)


  

## Contributing
We welcome contributions! To get started:
1. Fork the repository.
2. Create a branch: `git checkout -b feature/your-feature-name`.
3. Commit changes: `git commit -m "Add your feature"`.
4. Push to your branch: `git push origin feature/your-feature-name`.
5. Submit a pull request.

