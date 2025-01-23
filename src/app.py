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
from models import db, User, Character, Planet, Vehicle, Favorite
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

#Endpoints de los personajes

#Crear un personaje
@app.route('/people', methods=['POST'])
def create_character():
    try:
        body = request.get_json() 
        if not body or "name" not in body or "gender" not in body or "hair_color" not in body or "description" not in body:
            return jsonify({"msg": "Invalid input"}), 400

        new_people = Character(
            name=body["name"],
            description=body["description"],
            gender=body["gender"],
            hair_color=body["hair_color"]
        )
        db.session.add(new_people)
        db.session.commit()
        return jsonify({"msg": "Character has been created successfully"}), 201
    except Exception as error:
        return jsonify({"msg": "Server error", "error": str(error)}), 500

#Actualizar personaje por id
@app.route('/people/edit/<int:people_id>', methods=['PUT'])
def update_one_people(people_id):
    try:
        people = Character.query.get(people_id)
        if people is None:
            return jsonify({"msg": f"People {people_id} not found"}), 404

        body = request.get_json()
        people.name = body.get("name", people.name)
        people.gender = body.get("gender", people.gender)
        people.hair_color = body.get("hair_color", people.hair_color)

        db.session.commit()
        return people.serialize(), 200

    except Exception as error:
        return jsonify({"msg": "Server error", "error": str(error)}), 500

#Toda la lista de personajes
@app.route('/people', methods=['GET'])
def get_all_people():
    people = Character.query.all()
    people_list = [person.serialize() for person in people]
    return jsonify(people_list), 200


#Solo un personaje según id
@app.route('/people/<int:people_id>', methods=['GET'])
def get_people_by_id(people_id):
    person = Character.query.get(people_id)
    if person is None:
        return jsonify({"msg": "Character not found"}), 404
    return jsonify(person.serialize()), 200


#Endpoints de planetas

#Crear planeta
@app.route('/planets', methods=['POST'])
def create_one_planet():
    try:
        body = request.get_json() 
        if not body or "name" not in body or "population" not in body or "climate" not in body or "terrain" not in body:
            return jsonify({"msg": "Invalid input"}), 400

        new_planet = Planet(
            name=body["name"],
            population=body["population"],
            terrain=body["terrain"],
            climate=body["climate"]
        )
        db.session.add(new_planet)
        db.session.commit()
        return jsonify({"msg": "Planet has been created successfully"}), 201
    except Exception as error:
        return jsonify({"msg": "Server error", "error": str(error)}), 500

#Editar planeta por id
@app.route('/planet/edit/<int:planet_id>', methods=['PUT'])
def update_one_planet(planet_id):
    try:
        planet = Planet.query.get(planet_id)
        if planet is None:
            return jsonify({"msg": f"Planet {planet_id} not found"}), 404

        body = request.get_json()
        planet.name = body.get("name", planet.name)
        planet.population = body.get("population", planet.population)
        planet.climate = body.get("climate", planet.climate)

        db.session.commit()
        return planet.serialize(), 200

    except Exception as error:
        return jsonify({"msg": "Server error", "error": str(error)}), 500
    
#Todos los planetas
@app.route('/planets', methods=['GET'])
def get_all_planets():
    planets = Planet.query.all()
    planet_list = [planet.serialize() for planet in planets]
    return jsonify(planet_list), 200

#Solo un planeta por id
@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet_by_id(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({"msg": "Planet not found"}), 404
    return jsonify(planet.serialize()), 200

#Para crear un usuario
@app.route('/users', methods=['POST'])
def create_user():
    try:
        body = request.get_json()  
        if not body or "email" not in body or "password" not in body:
            return jsonify({"msg": "Invalid input"}), 400

        new_user = User(
            email=body["email"],
            password=body["password"],
            is_active=True
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"msg": "User has been created successfully"}), 201
    except Exception as error:
        return jsonify({"msg": "Server error", "error": str(error)}), 500
    
#Para editar un usuario
@app.route('/users/edit/<int:user_id>', methods=['PUT'])
def update_one_user(user_id):
    try:
        user = User.query.get(user_id)
        if user is None:
            return jsonify({"msg": f"User {user_id} not found"}), 404

        body = request.get_json()
        user.email = body.get("email", user.email)
        user.password = body.get("password", user.password)
        
        db.session.commit()
        return user.serialize(), 200

    except Exception as error:
        return jsonify({"msg": "Server error", "error": str(error)}), 500

#Para todos los usuarios
@app.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    user_list = [user.serialize() for user in users]
    return jsonify(user_list), 200

#Para un solo usuario
@app.route('/users/<int:user_id>', methods=['GET'])
def get_one_user(user_id):
    try:
        user = User.query.get(user_id)
        if user is None:
            return jsonify ({"msg":f"user {user_id} not found"}), 404
        serialize_user = user.serialize()
        return serialize_user, 200
    except Exception as error: 
        return jsonify ({"msg":"Server error", "error": str(error)}), 500

#Para los favoritos de un solo usuario
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

#Endpoints para vehiculos
#Para crear vehiculos
@app.route('/vehicles', methods=['POST'])
def create_one_vehicle():
    try:
        body = request.get_json()
        if not body or "name" not in body or "cargo_capacity" not in body or "length" not in body:
            return jsonify({"msg": "Invalid input"}), 400

        new_vehicle = Vehicle(
            name=body["name"],
            cargo_capacity=body["cargo_capacity"],
            length=body["length"]
        )
        db.session.add(new_vehicle)
        db.session.commit()
        return jsonify({"msg": "Vehicle has been created successfully"}), 201
    except Exception as error:
        return jsonify({"msg": "Server error", "error": str(error)}), 500

#Para editar vehiculos
@app.route('/edit/vehicle/<int:vehicle_id>', methods=['PUT'])
def update_one_vehicle(vehicle_id):
    try:
        vehicle = Vehicle.query.get(vehicle_id)
        if vehicle is None:
            return jsonify({"msg": f"Vehicle {vehicle_id} not found"}), 404

        body = request.get_json()
        vehicle.name = body.get("name", vehicle.name)
        vehicle.cargo_capacity = body.get("cargo_capacity", vehicle.cargo_capacity)
        vehicle.length = body.get("length", vehicle.length)

        db.session.commit()
        return vehicle.serialize(), 200

    except Exception as error:
        return jsonify({"msg": "Server error", "error": str(error)}), 500
    
#Para obtener todos los vehiculos
@app.route('/vehicles', methods=['GET'])
def get_all_vehicles():
    vehicles = Vehicle.query.all()
    vehicle_list = [vehicle.serialize() for vehicle in vehicles]
    return jsonify(vehicle_list), 200

#Para obtener un solo vehiculo por id
@app.route('/vehicles/<int:vehicle_id>', methods=['GET'])
def get_one_vehicle(vehicle_id):
    try:
        vehicle = Vehicle.query.get(vehicle_id)
        if vehicle is None:
            return jsonify ({"msg":f"Vehicle {vehicle_id} not found"}), 404
        serialize_vehicle = vehicle.serialize()
        return serialize_vehicle, 200
    except Exception as error:
        return jsonify ({"msg":"Server error", "error": str(error)}), 500
    

#Endpoints de favoritos

#Para todos los favoritos de un usuario
@app.route('/users/<int:user_id>/favorites', methods=['GET'])
def get_favorites_of_user_id(user_id):
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({"msg": "The user dont exist"}), 404

        if len(user.favorites)<1:
            return jsonify({"msg": "There are no favorites on the list"}), 404
        serialize_favorites = user.serialize_favorites()
        return serialize_favorites, 200
    except Exception as error: 
        return jsonify ({"msg":"Server error", "error": str(error)}), 500

#Crear vehiculo favorito
@app.route('/favorite/vehicle/<int:vehicle_id>/<int:user_id>', methods=['POST'])
def create_favorite_vehicle(vehicle_id, user_id):
    try:
        if Favorite.query.filter_by(user_id = user_id,vehicle_id=vehicle_id).first():
            return jsonify({"msg": f"Vehicle {vehicle_id} ya está agregago a favoritos"}), 404

        new_favorite_vehicle = Favorite(
            user_id=user_id,
            vehicle_id=vehicle_id
        )
        db.session.add(new_favorite_vehicle)
        db.session.commit()

        return jsonify({"msg": "Favorite Vehicle has been created successfully"}), 201
    except Exception as error:
        return jsonify({"msg": "Server error", "error": str(error)}), 500
    
#Para crear personaje favorito
@app.route('/favorite/people/<int:people_id>/<int:user_id>', methods=['POST'])
def create_favorite_people(people_id, user_id):
    try:
        if Favorite.query.filter_by(user_id = user_id,people_id=people_id).first():
            return jsonify({"msg": f"People {people_id} ya está agregago a favoritos"}), 404

        new_favorite_people = Favorite(
            user_id=user_id,
            people_id=people_id
        )
        db.session.add(new_favorite_people)
        db.session.commit()

        return jsonify({"msg": "Favorite Character has been created successfully"}), 201
    except Exception as error:
        return jsonify({"msg": "Server error", "error": str(error)}), 500

#Para crear planeta favorito
@app.route('/favorite/planet/<int:planet_id>/<int:user_id>', methods=['POST'])
def create_favorite_planet(planet_id, user_id):
    try:
        if Favorite.query.filter_by(user_id = user_id,planet_id=planet_id).first():
            return jsonify({"msg": f"Planet {planet_id} ya está agregago a favoritos"}), 404

        new_favorite_planet = Favorite(
            user_id=user_id,
            planet_id=planet_id
        )
        db.session.add(new_favorite_planet)
        db.session.commit()

        return jsonify({"msg": "Favorite Planet has been created successfully"}), 201
    except Exception as error:
        return jsonify({"msg": "Server error", "error": str(error)}), 500

#Para eliminar un vehiculo favorito
@app.route('/favorite/vehicle/<int:vehicle_id>/<int:user_id>', methods=['DELETE'])
def delete_favorite_vehicle(vehicle_id, user_id):
    try:
        elimate_favorite_vehicle = Favorite.query.filter_by(user_id=user_id, vehicle_id=vehicle_id).first()
        
        if not elimate_favorite_vehicle:
            return jsonify({"msg": f"Vehicle {vehicle_id} no se encuentra en los favoritos del usuario {user_id}"}), 404

        db.session.delete(elimate_favorite_vehicle)
        db.session.commit()

        return jsonify({"msg": f"Vehicle {vehicle_id} eliminado de los favoritos exitosamente"}), 200

    except Exception as error:
        return jsonify({"msg": "Server error", "error": str(error)}), 500

#Para eliminar planeta favorito
@app.route('/favorite/planets/<int:planet_id>/<int:user_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id, user_id):
    try:
        elimate_favorite_planet = Favorite.query.filter_by(user_id=user_id, planet_id=planet_id).first()
        
        if not elimate_favorite_planet:
            return jsonify({"msg": f"Planet {planet_id} no se encuentra en los favoritos del usuario {user_id}"}), 404

        db.session.delete(elimate_favorite_planet)
        db.session.commit()

        return jsonify({"msg": f"Planet {planet_id} eliminado de los favoritos exitosamente"}), 200

    except Exception as error:
        return jsonify({"msg": "Server error", "error": str(error)}), 500

#Para eliminar personaje favorito
@app.route('/favorite/people/<int:people_id>/<int:user_id>', methods=['DELETE'])
def delete_favorite_people(people_id, user_id):
    try:
        elimate_favorite_people = Favorite.query.filter_by(user_id=user_id, people_id=people_id).first()
        
        if not elimate_favorite_people:
            return jsonify({"msg": f"People {people_id} no se encuentra en los favoritos del usuario {user_id}"}), 404

        db.session.delete(elimate_favorite_people)
        db.session.commit()

        return jsonify({"msg": f"People {people_id} eliminado de los favoritos exitosamente"}), 200

    except Exception as error:
        return jsonify({"msg": "Server error", "error": str(error)}), 500

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
