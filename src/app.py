"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet, Favorite
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/people', methods=['GET'])
def get_all_people():
    people = Character.query.all()
    people_list = [person.serialize() for person in people]
    return jsonify(people_list), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def get_people_by_id(people_id):
    person = Character.query.get(people_id)
    if person is None:
        return jsonify({"msg": "Character not found"}), 404
    return jsonify(person.serialize()), 200

@app.route('/planets', methods=['GET'])
def get_all_planets():
    planets = Planet.query.all()
    planet_list = [planet.serialize() for planet in planets]
    return jsonify(planet_list), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet_by_id(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({"msg": "Planet not found"}), 404
    return jsonify(planet.serialize()), 200

@app.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    user_list = [user.serialize() for user in users]
    return jsonify(user_list), 200

@app.route('/users/<int:user_id>/favorites', methods=['GET'])
def get_user_favorites(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    favorites = Favorite.query.filter_by(user_id=user.id).all()
    if not favorites:
        return jsonify({"msg": "Not favorites found"}), 404
    favorites_list = [favorite.serialize() for favorite in favorites]
    return jsonify(favorites_list), 200

@app.route('/favorite/people/<int:people_id>', methods=['GET'])
def get_favorite_character(people_id):
    user_id = 1  # Example user ID
    favorite = Favorite.query.filter_by(user_id=user_id, character_id=people_id).first()
    
    if not favorite:
        return jsonify({"msg": "Favorite character not found"}), 404
    
    return jsonify(favorite.serialize()), 200

@app.route('/favorite/planets/<int:planet_id>', methods=['GET'])
def get_favorite_planet(planet_id):
    user_id = 1  # Example user ID
    favorite = Favorite.query.filter_by(user_id=user_id, planet_id=planet_id).first()

    if not favorite:
        return jsonify({"msg": "Favorite planet not found"}), 404

    return jsonify(favorite.serialize()), 200

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    user_id = 1  # Example user ID
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"msg": "Planet not found"}), 404
    existing_favorite = Favorite.query.filter_by(user_id=user.id, planet_id=planet.id).first()
    if existing_favorite:
        return jsonify({"msg": "Planet is already a favorite"}), 400
    new_favorite = Favorite(user_id=user.id, planet_id=planet.id)
    db.session.add(new_favorite)
    db.session.commit()
    return jsonify(new_favorite.serialize()), 201

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_character(people_id):
    user_id = 1  # Example user ID
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    character = Character.query.get(people_id)
    if not character:
        return jsonify({"msg": "Character not found"}), 404
    existing_favorite = Favorite.query.filter_by(user_id=user.id, character_id=character.id).first()
    if existing_favorite:
        return jsonify({"msg": "Character is already a favorite"}), 400
    new_favorite = Favorite(user_id=user.id, character_id=character.id)
    db.session.add(new_favorite)
    db.session.commit()
    return jsonify(new_favorite.serialize()), 201

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    user_id = 1  # Example user ID
    favorite = Favorite.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if not favorite:
        return jsonify({"msg": "Favorite planet not found"}), 404
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"msg": "Favorite planet was deleted"}), 200

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_character(people_id):
    user_id = 1  # Example user ID
    favorite = Favorite.query.filter_by(user_id=user_id, character_id=people_id).first()
    if not favorite:
        return jsonify({"msg": "Favorite character not found"}), 404
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"msg": "Favorite character was deleted"}), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
