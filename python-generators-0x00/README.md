# Database Seeding Utility

## Overview
This Python script sets up a MySQL database (`ALX_prodev`) with a `user_data` table and populates it with sample data from a CSV file. It provides a complete solution for initializing the database environment required for subsequent generator-based data streaming tasks.

## Features
- MySQL database connection management
- Database and table creation
- CSV data ingestion with duplicate prevention
- Modular design for easy integration

## Prerequisites
- Python 3.6+
- MySQL Server 5.7+
- `mysql-connector-python` package
- CSV data file (`user_data.csv`)

## Installation
Install dependencies:
   ```bash
   pip install mysql-connector-python python-dotenv
   ```
Set up environment variables (optional):
   ```bash
   echo "DB_USER=your_username" > .env
   echo "DB_PASSWORD=your_password" >> .env
