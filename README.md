## Requirements

- MySQL
- `mysql.connector` python module

Commands to be run in MySQL CLI for setup:

```
CREATE USER 'quiz_user'@'localhost' IDENTIFIED BY 'quiz123';

GRANT ALL PRIVILEGES ON quiz_app.* TO 'quiz_user'@'localhost';

FLUSH PRIVILEGES;
```
