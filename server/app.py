#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        json = request.get_json()
        username = json.get('username')
        password = json.get('password')
        image_url = json.get('image_url')
        bio = json.get('bio')
        new_user = User(
            username = username,
            image_url = image_url,
            bio = bio
        )  
        new_user.password_hash = password  
        try:
            db.session.add(new_user)
            db.session.commit()
            session['user_id'] = new_user.id
            return new_user.to_dict(), 201
        except IntegrityError:
            return {'error': '422 Unprocessable Entity'}, 422

class CheckSession(Resource):
    def get(self):
        user_id = session['user_id']
        if user_id:
            user = User.query.filter(User.id == user_id).first()
            return user.to_dict(), 200
        
        return {'error' : 'Unauthorized'}, 401

class Login(Resource):
    def post(self):
        username = request.get_json()['username']
        user = User.query.filter(User.username == username).first()

        password = request.get_json()['password']
        if user:
            if user.authenticate(password):
                session['user_id'] = user.id
                return user.to_dict(), 200
        return {'error' : 'invalid username or password'}, 401

class Logout(Resource):
    def delete(self):
        if session.get('user_id'):
            session['user_id'] = None
            return {}, 204
        return {'error': 'Unauthorized access'}, 401
        
        

class RecipeIndex(Resource):
    def get(self):
        
        if session.get('user_id') == None:
            return {'error': 'Unauthorized'}, 401
        else:
            return [recipe.to_dict() for recipe in Recipe.query.all()]
           

    def post(self):

        if not session['user_id']:
            return {'error': 'Unauthorized'}, 401
        if session['user_id']:

            json = request.get_json()
            try:
                recipe = Recipe(
                    title=json['title'],
                    instructions=json['instructions'],
                    minutes_to_complete=json['minutes_to_complete'],
                    user_id=session['user_id']
                )
                db.session.add(recipe)
                db.session.commit()
                return recipe.to_dict(), 201
            except IntegrityError:
                return {'error': 'Unprocessable Entity'}, 422
        
    
        


        

         

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
