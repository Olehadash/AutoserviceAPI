from AutoserviceAPI import app, db, allowed_file, login_manager, start_verification, check_verification, user_datastore, socketio
from flask import Flask, url_for, redirect, render_template, request, abort, jsonify
from AutoserviceAPI.model import User, Role, City, Category, Order, Recalls, Chats
from flask_login import login_user, logout_user, login_required
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from flask_socketio import SocketIO, emit, send, disconnect
from sqlalchemy import or_


@app.route('/get_chats', methods=['POST'])
@jwt_required()
def get_chats():
    phone = get_jwt_identity()
    user = User.query.filter_by(phone=phone).first()
    chats = Chats.query.filter(or_(Chats.user_id == user.id, Chats.customer_id == user.id)).first()

    return jsonify(chats = [i.serialize for i in chats]),200


    

@socketio.on('connect')
def connect():
    print('Client connected')

@socketio.on('disconnect')
def disconnect():
    print('Client disconnected')


@socketio.on('message')
def handle_message(data):
    print('received message: ' + data)
    emit('message', data, broadcast=True)
