from flask import Flask
from routes.auth import auth_bp
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

app.register_blueprint(auth_bp, url_prefix='/auth')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)