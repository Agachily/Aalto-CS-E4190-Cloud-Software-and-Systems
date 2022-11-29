from flask import Flask, jsonify, request, Response
from database.db import initialize_db
from database.models import Photo, Album
import json
from bson.objectid import ObjectId
import os
import urllib
import base64
import codecs

app = Flask(__name__)

# database configs
app.config['MONGODB_SETTINGS'] = {
    # set the correct parameters here as required, some examples are give below
    'host':'mongodb://mongo:27017/flask-database'
    #'host':'mongodb://localhost/flask-database'
}
db = initialize_db(app)

def str_list_to_objectid(str_list):
    return list(
        map(
            lambda str_item: ObjectId(str_item),
            str_list
        )
    )
@app.route('/listPhoto', methods=['POST'])
def add_photo():
    posted_image = request.files['file']
    posted_data = request.form
    name = posted_data.get('name')
    tags = posted_data.get('tags')
    if tags != None:
        tags = list(tags)
    location = posted_data.get('location')
    albums = posted_data.get('albums')
    def_albums = Album.objects(name='Default')
    if def_albums: 
        photo = Photo(name=name, tags=tags, location=location, albums=albums, image_file=posted_image)
        photo.save()
        id = str(photo.id)
        output = {'message': "Photo successfully created", 'id': id}
        return jsonify(output), 201
    else:
        album = Album(name='Default')
        album.save()
        photo = Photo(name=name, tags=tags, location=location, albums=albums, image_file=posted_image)
        photo.save()
        #photo.image_file.replace(posted_image)
        id = str(photo.id)
        output = {'message': "Photo successfully created", 'id': id}
        return jsonify(output), 201

@app.route('/listPhoto/<photo_id>', methods=['PUT'])
def update_photo(photo_id):
    posted_data = request.json
    name = posted_data.get('name')
    tags = posted_data.get('tags')
    location = posted_data.get('location')
    albums = posted_data.get('albums')
    photo = Photo.objects.get(id=photo_id)
    if name != None:
        photo.name = name
    if tags != None:
        photo.tags = tags
    if location != None:
        photo.location = location
    if albums != None:
        albums = str_list_to_objectid(albums)
        photo.albums = albums     
    photo.save()
    output = {'message':'Photo successfully updated', 'id':photo_id}
    return jsonify(output), 200

@app.route('/listPhotos', methods=['GET'])
def getByTag():
    tag = request.args.get('tag')
    albumName = request.args.get('albumName')
    photo_objects = None
    if tag != None:
        photo_objects = Photo.objects(tags=tag)
        #print(photo_objects, flush=True)
        photos = []
        if photo_objects != None:
            for photo in photo_objects:
                base64_data = codecs.encode(photo.image_file.read(), 'base64')
                image = base64_data.decode('utf-8')
                photos.append({'name': photo.name, 'location': photo.location, 'file': image})
        return jsonify(photos), 200
    if albumName != None:
        new_photo_objects = []
        photo_objects = Photo.objects()
        for photo in photo_objects:
            for album in photo.albums:
                if album.name == albumName:
                    new_photo_objects.append(photo)
        photos = []
        for photo in new_photo_objects:
            base64_data = codecs.encode(photo.image_file.read(), 'base64')
            image = base64_data.decode('utf-8')
            photos.append({'name': photo.name, 'location': photo.location, 'file': image})
        return jsonify(photos), 200


@app.route('/listPhoto/<photo_id>', methods=['GET'])
def get_photo(photo_id):
    photo = Photo.objects.get(id=photo_id)
    base64_data = codecs.encode(photo.image_file.read(), 'base64')
    image = base64_data.decode('utf-8')
    output = {'name': photo.name, 'tags': photo.tags, 'location': photo.location, 'albums': photo.albums, 'file':image}
    return jsonify(output), 200
    
@app.route('/listPhoto/<photo_id>', methods=['DELETE'])
def delete_photo(photo_id):
    photo = Photo.objects(id=photo_id)
    photo.delete()
    output = { 'message': 'Photo successfully deleted', 'id': photo_id }
    return jsonify(output), 200


@app.route('/listAlbum', methods=['POST'])
def album():
    name = request.json['name']
    des = request.json['description']
    album = Album(name=name, description=des)
    album.save()
    id = str(album.id)
    output = {'message': 'Album successfully created', 'id': id}
    return output, 201

@app.route('/listAlbum/<album_id>', methods=['DELETE'])
def albumDelete(album_id):
    album = Album.objects(id=album_id)
    if album:
        album.delete()
        output = {'message': 'Album successfully deleted', 'id': album_id}
        return jsonify(output), 200
    else:
        output = {'message': 'Not exist'}
        return jsonify(output), 404

@app.route('/listAlbum/<album_id>', methods=['GET'])
def albumGet(album_id):
    album = Album.objects.get(id=album_id)
    if album:
        output = {'id': album_id, 'name':album.name}
        return jsonify(output), 200
    else:
        output = {'message': 'Not exist'}
        return jsonify(output), 404   

@app.route('/listAlbum/<album_id>', methods=['PUT'])
def albumUpdate(album_id):
    album = Album.objects.get(id=album_id)
    if album:
        album.name = request.json['name']
        album.description = request.json['description']
        album.save()
        output = {'message': 'Album successfully updated', 'id': album_id}
        return jsonify(output), 200
    else:
        output = {'message': 'Not exist'}
        return jsonify(output), 404

@app.route('/')
def hello():
    return 'Hello hddeeedole world'