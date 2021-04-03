from AutoserviceAPI import app, db, allowed_file, login_manager, start_verification, check_verification
from flask import Flask, url_for, redirect, render_template, request, abort, jsonify
from AutoserviceAPI.model import City, Category
from flask_login import login_user, logout_user, login_required
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

@app.route('/get_cityes')
def get_cityes():
    city = City.query.all()
    return jsonify(cityes = [i.serialize for i in city]),200

@app.route('/get_categories')
def get_categories():
    category = Category.query.all()
    return jsonify(categories = [i.serialize for i in category]),200