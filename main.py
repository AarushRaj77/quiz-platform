import mysql.connector

db = mysql.connector.connect(host="localhost", user="quiz_user", password="quiz123")

cursor = db.cursor()

cursor.execute("CREATE DATABASE IF NOT EXISTS quiz_app")
cursor.execute("USE quiz_app")

# table: users
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(40) NOT NULL UNIQUE,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        type VARCHAR(10) NOT NULL DEFAULT 'student',
        email VARCHAR(100) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL
    );
""")

cursor.execute("INSERT IGNORE INTO users (username, type, email, password) values('{}', '{}', '{}','{}')".format("admin", "admin", "admin@mail.com", "admin"))
db.commit()

def initial_page():
    print("0: Log In \n1: Sign Up")
    option=int(input("Choose Your Option: "))

    if (option==0):
        if logged_in == False and current_user_type is None:
            login()
    elif (option==1):
        if logged_in == False and current_user_type is None:
            sign_up()
    else:
        pass

def login():
    l_name = input("Enter Username: ")
    l_password = input("Enter Password: ")

    query = "SELECT * FROM users WHERE username='{}'".format(l_name)
    cursor.execute(query)

    user = cursor.fetchone()

    if user:
        if l_password == user[5]:
            print("Login successful!")
            
            global username
            global logged_in
            global current_user_type

            logged_in=True
            current_user_type="student"
            username=l_name

            return 0
        else:
            print("Incorrect password!")
            login()
    else:
        print("Username does not exist!")
        login()


def sign_up():
    s_name=input("Your Username: ")
    s_email=input("Enter Your Email: ")
    s_password=input("Choose a Password to Confirm: ")
    
    if (s_name == "admin" or s_name == "" or s_password == "" or s_email == ""):
        print("Invalid Username/Email/Password")
        sign_up()

    try:
        cursor.execute(
            "INSERT INTO users (username, type, email, password) VALUES ('{}', '{}', '{}', '{}')".format(
                s_name, "student", s_email, s_password
            )
        )

        db.commit()
    except:
        print("Some Error Occurred")
        sign_up();

    db.commit()

    global username
    global logged_in
    global current_user_type

    logged_in=True
    current_user_type="student"
    username=s_name
    print("User Created & Logged In Successfully!")
    return 0

print("Welcome to Quiz Platform!")

logged_in=False
current_user_type=None
username=""

initial_page()

# print(logged_in, current_user_type, username)

cursor.close()
db.close()
