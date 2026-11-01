import mysql.connector 

db = mysql.connector.connect(host="localhost", user="quiz_user", password="quiz123") 

cursor = db.cursor() 

cursor.execute("CREATE DATABASE IF NOT EXISTS quiz_app") 
cursor.execute("USE quiz_app") 

# table: users 
cursor.execute("CREATE TABLE IF NOT EXISTS users ( 
    user_id INT AUTO_INCREMENT PRIMARY KEY,  
    username VARCHAR(40) NOT NULL UNIQUE, 
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,  
    type VARCHAR(10) DEFAULT 'student' NOT NULL, 
    email VARCHAR(100) NOT NULL UNIQUE, 
    password VARCHAR(255) NOT NULL )
")

cursor.close()
db.close()
