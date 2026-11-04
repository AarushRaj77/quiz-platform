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

# table: questions
cursor.execute("""
    CREATE TABLE IF NOT EXISTS questions (
        q_id INT AUTO_INCREMENT PRIMARY KEY,
        subject VARCHAR(40) NOT NULL,
        question TEXT NOT NULL,
        option_a VARCHAR(200) NOT NULL,
        option_b VARCHAR(200) NOT NULL,
        option_c VARCHAR(200) NOT NULL,
        option_d VARCHAR(200) NOT NULL,
        correct_option CHAR(1) NOT NULL,
        difficulty VARCHAR(20) DEFAULT 'Medium',
        marks INT DEFAULT 1
    );
""")

# table: quizzes
cursor.execute("""
    CREATE TABLE IF NOT EXISTS quizzes (
        quiz_id INT AUTO_INCREMENT PRIMARY KEY,
        quiz_name VARCHAR(100) NOT NULL,
        description TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS quiz_questions (
        quiz_id INT NOT NULL,
        q_id INT NOT NULL,
        question_order INT NOT NULL,

        PRIMARY KEY (quiz_id, q_id),

        FOREIGN KEY (quiz_id)
            REFERENCES quizzes(quiz_id)
            ON DELETE CASCADE,

        FOREIGN KEY (q_id)
            REFERENCES questions(q_id)
            ON DELETE CASCADE
    );
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS quiz_attempts (
        attempt_id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        quiz_id INT NOT NULL,
        score INT NOT NULL,
        total_marks INT NOT NULL,
        attempted_at DATETIME DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY (user_id)
            REFERENCES users(user_id)
            ON DELETE CASCADE,

        FOREIGN KEY (quiz_id)
            REFERENCES quizzes(quiz_id)
            ON DELETE CASCADE
    );
""");

cursor.execute("INSERT IGNORE INTO users (username, type, email, password) VALUES ('{}', '{}', '{}', '{}')".format("admin", "admin", "admin@mail.com", "admin"))

db.commit()

def initial_page():
    print("0: Log In \n1: Sign Up")
    option=int(input("Choose Your Option: "))

    if (option==0):
        if logged_in == False and current_user_type is None:
            login()
            return 0
    elif (option==1):
        if logged_in == False and current_user_type is None:
            sign_up()
            return 0
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
            current_user_type = user[3]
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
        return

    try:
        cursor.execute(
            "INSERT INTO users (username, type, email, password) VALUES ('{}', '{}', '{}', '{}')".format(
                s_name, "student", s_email, s_password
            )
        )

        db.commit()
    except:
        print("Some Error Occurred")
        return


    global username
    global logged_in
    global current_user_type

    logged_in=True
    current_user_type="student"
    username=s_name
    print("User Created & Logged In Successfully!")
    return 0


def admin_interface():
    print("\t0: Edit Existing Quizzes\n\t1: Create a Quiz\n\t2: Add Questions to Question Bank\n\t3: See Student Analytics\n\t4: Exit")
    option=int(input("Choose Your Option: "))

    if (option == 0):
        cursor.execute("SELECT * FROM quizzes")
        quizzes = cursor.fetchall()

        if not quizzes:
            print("No quizzes available!")
            return

        print("AVAILABLE QUIZZES:")

        for quiz in quizzes:
            print("\nQuiz ID:", quiz[0])
            print("Quiz Name:", quiz[1])
            print("Description:", quiz[2])
            print("Created At:", quiz[3])

            cursor.execute("""
                SELECT q.q_id, q.subject, q.question, qq.question_order
                FROM questions q
                JOIN quiz_questions qq ON q.q_id = qq.q_id
                WHERE qq.quiz_id = {}
                ORDER BY qq.question_order
            """.format(quiz[0]))

            quiz_questions = cursor.fetchall()

            print("\nQuestions:")

            for q in quiz_questions:
                print("\n  Question ID:", q[0])
                print("  Subject:", q[1])
                print("  Question:", q[2])
                print("  Order:", q[3])

            print("\n" + "-" * 45)

        edit_id = int(input("\nEnter Quiz ID to edit (0 to go back): "))

        if edit_id == 0:
            return

        cursor.execute("SELECT * FROM quizzes WHERE quiz_id = {}".format(edit_id))
        selected_quiz = cursor.fetchone()

        if selected_quiz:
            print("\nSelected Quiz:", selected_quiz[1])

            editing = True

            while editing:
                print("""
    Edit a Quiz:
    \t0: Change Quiz Name
    \t1: Change Description
    \t2: Add Questions
    \t3: Remove Questions
    \t4: Reorder Questions
    \t5: Delete Quiz
    \t6: Back
    """)
                edit_option = int(input("Choose Your Option: "))

                if edit_option == 0:
                    new_name = input("Enter New Quiz Name: ")

                    cursor.execute("""
                        UPDATE quizzes
                        SET quiz_name = '{}'
                        WHERE quiz_id = {}
                    """.format(new_name.replace("'", "''"), edit_id))

                    db.commit()
                    print("Quiz Name Updated!")

                elif edit_option == 1:
                    new_description = input("Enter New Description: ")

                    cursor.execute("""
                        UPDATE quizzes
                        SET description = '{}'
                        WHERE quiz_id = {}
                    """.format(new_description.replace("'", "''"), edit_id))

                    db.commit()
                    print("Description Updated!")

                elif edit_option == 2:
                    print("\nAvailable Questions:")

                    cursor.execute("SELECT q_id, subject, question FROM questions")
                    available_questions = cursor.fetchall()

                    for q in available_questions:
                        print("\nID:", q[0])
                        print("Subject:", q[1])
                        print("Question:", q[2])

                    q_id = int(input("\nEnter Question ID to add: "))

                    cursor.execute("""
                        SELECT q_id FROM questions
                        WHERE q_id = {}
                    """.format(q_id))

                    if cursor.fetchone():
                        cursor.execute("""
                            SELECT q_id FROM quiz_questions
                            WHERE quiz_id = {} AND q_id = {}
                        """.format(edit_id, q_id))

                        if cursor.fetchone():
                            print("Question already exists in this quiz!")

                        else:
                            cursor.execute("""
                                SELECT MAX(question_order)
                                FROM quiz_questions
                                WHERE quiz_id = {}
                            """.format(edit_id))

                            result = cursor.fetchone()
                            question_order = result[0]

                            if question_order is None:
                                question_order = 1
                            else:
                                question_order += 1

                            cursor.execute("""
                                INSERT INTO quiz_questions
                                (quiz_id, q_id, question_order)
                                VALUES ({}, {}, {})
                            """.format(edit_id, q_id, question_order))

                            db.commit()
                            print("Question Added Successfully!")

                    else:
                        print("Question ID does not exist!")

                elif edit_option == 3:
                    cursor.execute("""
                        SELECT q.q_id, q.question, qq.question_order
                        FROM questions q
                        JOIN quiz_questions qq ON q.q_id = qq.q_id
                        WHERE qq.quiz_id = {}
                        ORDER BY qq.question_order
                    """.format(edit_id))

                    quiz_questions = cursor.fetchall()

                    if not quiz_questions:
                        print("This quiz has no questions!")
                    else:
                        for q in quiz_questions:
                            print("\nID:", q[0])
                            print("Question:", q[1])
                            print("Order:", q[2])

                        q_id = int(input("\nEnter Question ID to remove: "))

                        cursor.execute("""
                            DELETE FROM quiz_questions
                            WHERE quiz_id = {} AND q_id = {}
                        """.format(edit_id, q_id))

                        if cursor.rowcount > 0:
                            db.commit()

                            cursor.execute("""
                                SELECT q_id FROM quiz_questions
                                WHERE quiz_id = {}
                                ORDER BY question_order
                            """.format(edit_id))

                            remaining_questions = cursor.fetchall()

                            question_order = 1

                            for q in remaining_questions:
                                cursor.execute("""
                                    UPDATE quiz_questions
                                    SET question_order = {}
                                    WHERE quiz_id = {} AND q_id = {}
                                """.format(question_order, edit_id, q[0]))

                                question_order += 1

                            db.commit()
                            print("Question Removed Successfully!")

                        else:
                            print("Question not found in this quiz!")

                elif edit_option == 4:
                    cursor.execute("""
                        SELECT q.q_id, q.question, qq.question_order
                        FROM questions q
                        JOIN quiz_questions qq ON q.q_id = qq.q_id
                        WHERE qq.quiz_id = {}
                        ORDER BY qq.question_order
                    """.format(edit_id))

                    quiz_questions = cursor.fetchall()

                    if not quiz_questions:
                        print("This quiz has no questions!")

                    else:
                        for q in quiz_questions:
                            print("\nID:", q[0])
                            print("Question:", q[1])
                            print("Current Order:", q[2])

                        q_id = int(input("\nEnter Question ID to move: "))
                        new_order = int(input("Enter New Position: "))

                        question_ids = []

                        for q in quiz_questions:
                            question_ids.append(q[0])

                        if q_id not in question_ids:
                            print("Question not found!")

                        elif new_order < 1 or new_order > len(question_ids):
                            print("Invalid Position!")

                        else:
                            question_ids.remove(q_id)
                            question_ids.insert(new_order - 1, q_id)

                            question_order = 1

                            for q in question_ids:
                                cursor.execute("""
                                    UPDATE quiz_questions
                                    SET question_order = {}
                                    WHERE quiz_id = {} AND q_id = {}
                                """.format(question_order, edit_id, q))

                                question_order += 1

                            db.commit()
                            print("Question Order Updated!")

                elif edit_option == 5:
                    confirm = input("Are you sure you want to delete this quiz? (yes/no): ")

                    if confirm.lower() == "yes":
                        cursor.execute("""
                            DELETE FROM quizzes
                            WHERE quiz_id = {}
                        """.format(edit_id))

                        db.commit()
                        print("Quiz Deleted Successfully!")
                        editing = False

                elif edit_option == 6:
                    editing = False

                else:
                    print("Invalid Option!")

        else:
            print("Invalid Quiz ID!")
    elif (option == 1):
        quiz_name = input("Enter Quiz Name: ")
        description = input("Enter Quiz Description: ")

        print("\nAvailable Questions:")

        cursor.execute("SELECT q_id, subject, question FROM questions")
        available_questions = cursor.fetchall()

        for q in available_questions:
            print("ID: {} | Subject: {} | Question: {}".format(q[0], q[1], q[2]))

        q_ids = input("\nEnter Question IDs (comma separated): ")
        q_ids = q_ids.split(",")

        cursor.execute("""
            INSERT INTO quizzes (quiz_name, description)
            VALUES ('{}', '{}')
        """.format(quiz_name, description))

        quiz_id = cursor.lastrowid

        question_order = 1

        for q_id in q_ids:
            q_id = int(q_id.strip())

            cursor.execute("""
                INSERT INTO quiz_questions (quiz_id, q_id, question_order)
                VALUES ({}, {}, {})
            """.format(quiz_id, q_id, question_order))

            question_order += 1

        db.commit()

        print("\nQuiz Created Successfully!")
        print("Quiz ID:", quiz_id)
        print("Total Questions:", len(q_ids))
    elif (option == 2):
        subject = input("Enter Subject: ")
        question = input("Enter Question: ")

        option_a = input("Option A: ")
        option_b = input("Option B: ")
        option_c = input("Option C: ")
        option_d = input("Option D: ")

        correct_option = input("Correct Option (A/B/C/D): ").upper()
        difficulty = input("Difficulty (Easy/Medium/Hard): ")
        marks = int(input("Marks: "))

        if correct_option not in ('A', 'B', 'C', 'D'):
            print("Invalid Correct Option!")
            return

        cursor.execute("""
            INSERT INTO questions
            (subject, question, option_a, option_b, option_c, option_d,
             correct_option, difficulty, marks)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            subject, question, option_a, option_b, option_c, option_d,
            correct_option, difficulty, marks
        ))

    elif (option == 4):
        global is_running
        is_running=False
    else:
        pass

def student_interface():
    print("0: Attempt a Quiz\n1: See Your Performance\n2: Exit")
    option=int(input("Choose Your Option: "))

    if (option == 0):

        cursor.execute("SELECT * FROM quizzes")
        quizzes=cursor.fetchall()
        for quiz in quizzes:
            print(quiz[0] , ":", quiz[1], "(", quiz[2], ")")

        selected_quiz_id=input("Choose a quiz to attempt: ")

        cursor.execute("SELECT qq.q_id FROM quizzes qz, quiz_questions qq WHERE qz.quiz_id=qq.quiz_id and qq.quiz_id = {} ORDER BY qq.question_order".format(selected_quiz_id))

        ques_ids=[]
        data=cursor.fetchall()

        for d in data:
            ques_ids.append(d[0])

        cursor.execute("SELECT * FROM questions")
        all_ques_data=cursor.fetchall()

        quiz_ques_data=[]

        for i in ques_ids:
            for q in all_ques_data:
                if q[0] == i:
                    quiz_ques_data.append(q)

        total_marks=0

        for q in quiz_ques_data:
            total_marks+=q[9]

        marks_gained=0

        for question in quiz_ques_data:
            print("Q.", question[2])
            print("\tA.", question[3])
            print("\tB.", question[4])
            print("\tC.", question[5])
            print("\tD.", question[6])

            answer=input("Choose Your Answer: ").upper()
            print("\n")
            if (answer == question[7]):
                marks_gained+=question[9]

        print("---")
        print("YOUR SCORE:", marks_gained, "/", total_marks)
        print("---\n")

        cursor.execute("""
            SELECT user_id FROM users
            WHERE username = '{}'
        """.format(username))

        user_id = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO quiz_attempts
            (user_id, quiz_id, score, total_marks)
            VALUES ({}, {}, {}, {})
        """.format(user_id, selected_quiz_id, marks_gained, total_marks))

        db.commit()

    elif (option == 1):
        pass
    elif (option == 2):
        global is_running
        is_running=False
    else:
        pass

print("Welcome to Quiz Platform!")

logged_in=False
current_user_type=None
username=""

initial_page()

is_running=True

while(is_running):
    if (current_user_type == "admin" or username == "admin"):
        admin_interface()
    elif (current_user_type == "student" or username != "admin"):
        student_interface()


cursor.close()
db.close()
