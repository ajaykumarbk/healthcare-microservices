import uuid
from flask_bcrypt import Bcrypt
from mysql.connector import connect, Error

bcrypt = Bcrypt()

class User:
    def __init__(self, db_config):
        self.db_config = db_config

    def create(self, email, password, role):
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        user_id = str(uuid.uuid4())
        try:
            with connect(**self.db_config) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (id, email, password_hash, role) VALUES (%s, %s, %s, %s)",
                    (user_id, email, password_hash, role)
                )
                conn.commit()
                return user_id
        except Error as e:
            raise Exception(f"Database error: {e}")

    def find_by_email(self, email):
        try:
            with connect(**self.db_config) as conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                return cursor.fetchone()
        except Error as e:
            raise Exception(f"Database error: {e}")

    def verify_password(self, password, password_hash):
        return bcrypt.check_password_hash(password_hash, password)