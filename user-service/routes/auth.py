from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from models.user import User
from models.audit_log import AuditLog
import uuid
import datetime

auth_bp = Blueprint('auth', __name__)
db_config = {
    'host': Config.MYSQL_HOST,
    'user': Config.MYSQL_USER,
    'password': Config.MYSQL_PASSWORD,
    'database': Config.MYSQL_DB
}
user_model = User(db_config)
audit_log_model = AuditLog(db_config)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')

    if not email or not password or not role:
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        user_id = user_model.create(email, password, role)
        audit_log_model.log(user_id, 'register', request.remote_addr, {'email': email})
        return jsonify({'message': 'User registered', 'user_id': user_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Missing required fields'}), 400

    user = user_model.find_by_email(email)
    if not user or not user_model.verify_password(password, user['password_hash']):
        audit_log_model.log(None, 'failed_login', request.remote_addr, {'email': email})
        return jsonify({'error': 'Invalid credentials'}), 401

    access_token = create_access_token(identity=user['id'], additional_claims={'role': user['role']})
    refresh_token = create_refresh_token(identity=user['id'])
    audit_log_model.log(user['id'], 'login', request.remote_addr, {'email': email})

    return jsonify({'access_token': access_token, 'refresh_token': refresh_token}), 200

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    access_token = create_access_token(identity=user_id)
    return jsonify({'access_token': access_token}), 200

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    user = user_model.find_by_email(user_id)
    return jsonify({'user_id': user['id'], 'email': user['email'], 'role': user['role']}), 200