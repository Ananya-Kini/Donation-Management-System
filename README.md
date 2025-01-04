# Donation-Management-System
The Donation Management System is a web application designed to manage donations and sponsorships efficiently. This system helps NGOs streamline their donation processes, track contributions, and engage with donors effectively. Main features are Donor Interaction, Child sponsorships and Inventory management. Donors can browse campaigns, make donations, and view their donation history. Fieldworkers have access to details about the inventory banks, and children who are in need of sponsorships. 

## Installation

1. Create a Django Project:
Use the following commands to set up a new Django project and app:

django-admin startproject projectname
cd projectname
python manage.py startapp appname

This will create the necessary project and app directories.

2. Clone the Repository:
Clone this repository and move all the files into your project folder. Adjust folder names if required to fit your project structure.

3. Configure MySQL Settings:
In minii/settings.py, update the database configuration with your MySQL username, password, and database name. This ensures the application connects to the correct database.

4. Prepare the Database:
Run the following commands to generate and apply migrations for the database:

python manage.py makemigrations
python manage.py migrate

Start the Development Server:
Launch the application by running:

python manage.py runserver

Navigate to the provided address in your web browser to access the application.
