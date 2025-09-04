import uuid
from mysql.connector import connect, Error

class AuditLog:
    def __init__(self, db_config):
        self.db_config = db_config

    def log(self, user_id, event_type, ip_address, details):
        try:
            with connect(**self.db_config) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO audit_logs (id, user_id, event_type, ip_address, details) VALUES (%s, %s, %s, %s, %s)",
                    (str(uuid.uuid4()), user_id, event_type, ip_address, json.dumps(details))
                )
                conn.commit()
        except Error as e:
            raise Exception(f"Database error: {e}")