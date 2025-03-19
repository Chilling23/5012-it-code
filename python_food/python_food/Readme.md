# Program Usage Guide

## 1. Admin Account for Backend Management

- **Username:** `admin123`
- **Password:** `admin123`

## 2. Code Structure

- **server** directory contains the backend code
- **web** directory contains the frontend code

## 3. Deployment and Running Steps

### Backend Running Steps

1. **Install Python 3.8**

2. **Install Dependencies:** Enter the `server` directory and run the following command:

   ```bash
   pip install -r requirements.txt
   ```

3. **Install MySQL 5.7 Database and Create Database**

   Run the following SQL command to create the database:

   ```sql
   CREATE DATABASE IF NOT EXISTS shop DEFAULT CHARSET utf8 COLLATE utf8_general_ci;
   ```

4. **Restore `shop.sql` Data**

   In MySQL, execute the following commands:

   ```sql
   mysql> use shop;
   mysql> source D:/xxx/xxx/xxx.sql;
   ```

5. **Start the Django Service**

   Enter the `server` directory and run:

   ```bash
   python manage.py runserver
   ```

### Frontend Running Steps

1. **Install Node.js 16.14**

2. **Install Dependencies:** Enter the `web` directory and run:

   ```bash
   npm install
   ```

3. **Run the Project**

   ```bash
   npm run dev
   ```

