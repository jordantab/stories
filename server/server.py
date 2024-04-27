from bson import ObjectId
from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient, ReturnDocument
from pymongo.server_api import ServerApi

def create_app():
    app = Flask(__name__)
    # CORS(app, resources={r"/stories": {"origins": "*"}})
    CORS(app, origins="*")

    uri = "mongodb+srv://temp_user:1234@stories.detzj4q.mongodb.net/?retryWrites=true&w=majority&appName=Stories"
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client.stories

    with app.app_context():
        try:
            client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(e)

    @app.route('/')
    def home():
        return 'Hello, World!'

    @app.route('/stories', methods=['GET'])
    def get_stories():
        print("Getting stories...\n")
        stories_collection = db.stories
        stories = list(stories_collection.find({}))

        stories_data = [{
            key: str(value) if isinstance(value, ObjectId) else value
            for key, value in story.items()
        } for story in stories]

        return jsonify(stories_data)

    @app.route('/stories/', methods=['POST'])
    def create_story():
        print("Creating story...\n")
        stories_collection = db.stories
        story_data = request.json
        print(story_data)

        if not story_data:
            return jsonify({"error": "No data provided"}), 400

        try:
            result = stories_collection.insert_one(story_data)
            new_story = stories_collection.find_one({'_id': result.inserted_id})
        except Exception as e:
            print(e)
            return jsonify({'error': 'Failed to create story'}), 500

        if new_story:
            new_story_data = {key: str(value) if isinstance(value, ObjectId) else value for key, value in new_story.items()}
            return jsonify({'message': 'Story created successfully', 'story': new_story_data}), 201
        else:
            return jsonify({'error': 'Failed to retrieve created story'}), 500

    @app.route('/stories/<story_id>', methods=['GET'])
    def get_story(story_id):
        stories_collection = db.stories

        try:
            oid = ObjectId(story_id)
            story = stories_collection.find_one({'_id': oid})
        except:
            return jsonify({'error': 'Invalid story story_id'}), 400

        if story:
            story_data = {key: str(value) if isinstance(value, ObjectId) else value for key, value in story.items()}
            return jsonify(story_data)
        else:
            return jsonify({'message': 'Story not found'}), 404

    @app.route('/leads', methods=['GET'])
    def get_leads():
        print("Getting leads...\n")
        leads_collection = db.leads
        leads = list(leads_collection.find({}))

        leads_data = [{
            key: str(value) if isinstance(value, ObjectId) else value
            for key, value in lead.items()
        } for lead in leads]

        return jsonify(leads_data)


    @app.route('/leads/', methods=['POST'])
    def create_lead():
        print("Creating lead...\n")
        leads_collection = db.leads
        lead_data = request.json
        print(lead_data)

        if not lead_data:
            return jsonify({"error": "No data provided"}), 400

        try:
            result = leads_collection.insert_one(lead_data)
            new_lead = leads_collection.find_one({'_id': result.inserted_id})
        except Exception as e:
            print(e)
            return jsonify({'error': 'Failed to create lead'}), 500

        if new_lead:
            new_lead_data = {key: str(value) if isinstance(value, ObjectId) else value for key, value in new_lead.items()}
            return jsonify({'message': 'lead created successfully', 'lead': new_lead_data}), 201
        else:
            return jsonify({'error': 'Failed to retrieve created lead'}), 500


    @app.route('/leads/<lead_id>', methods=['POST'])
    def update_lead(lead_id):
        print("Updating lead...\n")
        leads_collection = db.leads
        update_data = request.json

        try:
            oid = ObjectId(lead_id)
            result = leads_collection.find_one_and_update(
            {'_id': oid},
            {'$set': update_data},
            return_document=ReturnDocument.AFTER
        )
        except Exception as e:
            return jsonify({'error': str(e)}), 400

        if result:
            updated_lead = {key: str(value) if isinstance(value, ObjectId) else value for key, value in result.items()}
            return jsonify(updated_lead)
        else:
            return jsonify({'message': 'Lead not found'}), 404
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
