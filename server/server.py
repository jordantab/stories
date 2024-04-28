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

    def convert_objectid_to_str(data):
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, ObjectId):
                    data[key] = str(value)
                elif isinstance(value, (dict, list)):
                    convert_objectid_to_str(value)
        elif isinstance(data, list):
            for index, item in enumerate(data):
                if isinstance(item, ObjectId):
                    data[index] = str(item)
                elif isinstance(item, (dict, list)):
                    convert_objectid_to_str(item)

    @app.route('/stories', methods=['GET'])
    def get_stories():
        print("Getting stories...\n")
        stories_collection = db.stories
        stories = list(stories_collection.find({}))

        stories_data = [{
            key: str(value) if isinstance(value, ObjectId) else value
            for key, value in story.items()
        } for story in stories]
        convert_objectid_to_str(stories_data)

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

        model_version = "text-embedding-ada-002"

        embeddings = []
        try:
            # Batch processing if needed, or processing one by one
            for text in text_list:
                response = openai.embeddings.create(
                input=text,
                model="text-embedding-ada-002"
                )
                # print(response.data)
                if response:
                    embeddings.append(response.data[0].embedding)
        except Exception as e:
            print(f"An error occurred while generating embeddings: {e}")
            raise

        return embeddings

    def generate_image(slide_text):
        openai.api_key = app.config['OPENAI_API_KEY']
        res = openai.chat.completions.create(
          model="gpt-3.5-turbo",
          messages=[
            {"role": "system", "content": "You are an image prompt helper who creates a prompt for an image generator which describes a sleek and beautiful visualization to go along with slide text"},
            {"role": "user", "content": slide_text}
          ]
        )
        image_prompt = res.choices[0].message.content
        response = openai.images.generate(
          model="dall-e-3",
          prompt=image_prompt,
          size="1024x1024",
          quality="standard",
          n=1,
        )
        image_url = response.data[0].url
        return image_url

#     test_text = """Organizations realize the value data plays as a strategic asset for various
# business-related initiatives, such as growing revenues, improving the customer
# experience, operating efficiently or improving a product or service. However,
# accessing and managing data for these initiatives has become increasingly
# complex. """
#     print(generate_image(test_text))
#     exit()

    def create_display_page(story_id, number, doc_text, role):
        openai.api_key = app.config['OPENAI_API_KEY']
        res = openai.chat.completions.create(
          model="gpt-3.5-turbo",
          messages=[
            {"role": "system", "content": role},
            {"role": "user", "content": doc_text}
          ]
        )
        slide_text = res.choices[0].message.content
        res = openai.chat.completions.create(
          model="gpt-3.5-turbo",
          messages=[
            {"role": "system", "content": "You are a title generator, give a good powerpoint slide title of maybe 5 words for the user's text. Do not include quotes."},
            {"role": "user", "content": slide_text}
          ]
        )
        slide_title = res.choices[0].message.content
        fourth_page = {}
        fourth_page["story_id"] = story_id
        fourth_page["number"] = number
        fourth_page["title"] = slide_title
        fourth_page["text"] = slide_text
        fourth_page["type"] = "display"
        return fourth_page

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

        if not story_data:
            return jsonify({"error": "No story data provided"}), 400

        # Insert story metadata into MongoDB
        try:
            # Extract text from PDF and generate embeddings
            text_by_page = extract_text_from_pdf(file_path)
            # print("text_by_page", text_by_page)
            embeddings = generate_embeddings(text_by_page, app.config['OPENAI_API_KEY'])
            # print("embeddings", embeddings)

            # Include file path and embeddings in the story data
            story_data['file_path'] = file_path
            # story_data['embeddings'] = embeddings
            story_data['text_by_page'] = text_by_page

            # Insert story metadata and embeddings into MongoDB
            result = db.stories.insert_one(story_data)
            new_story = db.stories.find_one({'_id': result.inserted_id})

            new_page = {}
            new_page["story_id"] = new_story["_id"]
            new_page["number"] = 0
            new_page["title"] = story_data["name"]
            new_page["text"] = story_data["tagline"]
            new_page["type"] = "display"

            intro_text = text_by_page[0] + text_by_page[1] + text_by_page[2] + text_by_page[3]
            second_page = create_display_page(new_story["_id"], 1, intro_text, "You are a business analyst who provides the primary value prop of a document. Tell the user the main value proposition of what they say in about 30 words. Do not mention the document.")

            email_page = {}
            email_page["story_id"] = new_story["_id"]
            email_page["number"] = 2
            email_page["text"] = "Let's start with your email"
            email_page["query_key"] = "email"
            email_page["type"] = "query"

            full_text = " ".join(text_by_page)
            fourth_page = create_display_page(new_story["_id"], 3, full_text, "Talk about a few of the primary customers who see value from this kind of service in about 50 words")

            initial_pages = [new_page, second_page, email_page, fourth_page]
            db.stories.update_one(
                {"_id": new_story["_id"]},
                {"$set": {"pages": initial_pages}}
            )

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
            # print("STORY:", story)
        except:
            return jsonify({'error': 'Invalid story story_id'}), 400

        if story:
            story_data = {key: str(value) if isinstance(value, ObjectId) else value for key, value in story.items()}
            print("Returning story data")
            convert_objectid_to_str(story_data)
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
        print("Updating lead", lead_id, "with data", update_data)

        try:
            oid = ObjectId(lead_id)
            result = leads_collection.find_one_and_update(
            {'_id': oid},
            {'$set': update_data},
            return_document=ReturnDocument.AFTER
        )
        except Exception as e:
            return jsonify({'error': str(e)}), 400

        if "email" in update_data:
            print("Updating for email")
            domain = update_data["email"].split("@")[1]

            story_id = update_data["storyId"]
            print("storyId is:", story_id)
            story = db.stories.find_one({'_id': ObjectId(story_id)})
            print("story", story)
            full_text = " ".join(story["text_by_page"])
            page_five = create_display_page(story_id, 4, full_text, "Mention in about 30 words how our product has worked well for a similar company given that the user works for " + domain + ". Do not use quotes.")
            page_six = create_display_page(story_id, 5, full_text, "Mention in about 30 words how our product will solve the user's problems given that the user works for " + domain + ". Do not use quotes.")

            email_page = {}
            email_page["story_id"] = story_id
            email_page["number"] = 6
            email_page["text"] = "What is your role at " + domain + "?"
            email_page["query_key"] = "role"
            email_page["type"] = "query"

            page_eight = create_display_page(story_id, 7, full_text, "Mention in about 30 words how easy it is to use the product. Do not use quotes.")

            initial_pages = [page_five, page_six, email_page, page_eight]
            all_pages = story["pages"] + initial_pages
            print("all-pages:", all_pages)
            db.stories.update_one(
                {"_id": ObjectId(story_id)},
                {"$set": {"pages": all_pages}}
            )
            story = db.stories.find_one({'_id': ObjectId(story_id)})
            print("story", story)
        elif "role" in update_data:
            role = update_data["role"]

            story_id = update_data["storyId"]
            print("storyId is:", story_id)
            story = db.stories.find_one({'_id': ObjectId(story_id)})
            print("story", story)
            full_text = " ".join(story["text_by_page"])
            page_five = create_display_page(story_id, 8, full_text, "Mention in about 30 words how our product can really drive value for someone who works as a " + role + ". Do not use quotes.")
            page_six = create_display_page(story_id, 9, full_text, "Mention in about 30 words how our product has solved problems at other companies for people who work as a " + role + ". Do not use quotes.")

            initial_pages = [page_five, page_six]
            all_pages = story["pages"] + initial_pages
            print("all-pages:", all_pages)
            db.stories.update_one(
                {"_id": ObjectId(story_id)},
                {"$set": {"pages": all_pages}}
            )
            story = db.stories.find_one({'_id': ObjectId(story_id)})
            print("story", story)

        if result:
            updated_lead = {key: str(value) if isinstance(value, ObjectId) else value for key, value in result.items()}
            return jsonify(updated_lead)
        else:
            return jsonify({'message': 'Lead not found'}), 404
    # print("story", db.stories.find_one({'_id': ObjectId("662d9690f044ed09f58bbbb4")}))
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
