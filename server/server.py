from bson import ObjectId
from bson.json_util import dumps
from werkzeug.utils import secure_filename
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient, ReturnDocument
from pymongo.server_api import ServerApi
import PyPDF2
import openai
from dotenv import load_dotenv

def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = 'uploads/'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    app.config['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
    
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
    
    def allowed_file(filename):
        return '.' in filename and filename.lower().endswith('.pdf')

    def extract_text_from_pdf(filepath):
        print("Extracting text...\n", filepath)
        text_by_page = []
        with open(filepath, 'rb') as file:
            # print(1)
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                # print(2)
                page = pdf_reader.pages[page_num]
                try:
                    # print(3)
                    text = page.extract_text()
                    if text:
                        # print(4)
                        text_by_page.append(text)
                except Exception as e:
                    print(f"Failed to extract text from page {page_num}: {e}")
                    text_by_page.append("")
        # print(5)
        return text_by_page
    
    def generate_embeddings(text_list, openai_api_key):
        openai.api_key = openai_api_key

        # Adjusting to use the newer model as per the example provided
        model_version = "text-embedding-ada-002"  # Adjust model as necessary

        embeddings = []
        try:
            # Batch processing if needed, or processing one by one
            for text in text_list:
                response = openai.embeddings.create(
                input=text,
                model="text-embedding-ada-002"
                )
                print(response)
                if response and 'data' in response:
                    embeddings.append(response['data'][0]['embedding'])
        except Exception as e:
            print(f"An error occurred while generating embeddings: {e}")
            raise

        return embeddings

    @app.route('/stories/', methods=['POST'])
    def create_story():
        print("Creating story...\n")
        if 'file' not in request.files:
            return jsonify({"error": "No file part in the request"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected for uploading"}), 400

        # Save the PDF file
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            print(f"File {filename} uploaded successfully.")
        else:
            return jsonify({"error": "Allowed file types are pdf"}), 400

        # Parse additional story data from form or JSON
        story_data = request.form.to_dict()
        print(story_data)

        # if not story_data:
        #     return jsonify({"error": "No story data provided"}), 400

        # Insert story metadata into MongoDB
        try:
            # Extract text from PDF and generate embeddings
            text_by_page = extract_text_from_pdf(file_path)
            # print("text_by_page", text_by_page)
            embeddings = generate_embeddings(text_by_page, app.config['OPENAI_API_KEY'])
            print("embeddings", embeddings)

            # Include file path and embeddings in the story data
            story_data['file_path'] = file_path
            story_data['embeddings'] = embeddings

            # Insert story metadata and embeddings into MongoDB
            result = db.stories.insert_one(story_data)
            new_story = db.stories.find_one({'_id': result.inserted_id})
            
            if new_story:
                new_story_data = {key: str(value) if isinstance(value, ObjectId) else value for key, value in new_story.items()}
                return jsonify({'message': 'Story created successfully', 'story': new_story_data}), 201
            else:
                return jsonify({'error': 'Failed to retrieve created story'}), 500
        except Exception as e:
            print(e)
            return jsonify({'error': 'Failed to create story'}), 500

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
