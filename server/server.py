from flask import Flask
from pymongo import MongoClient
from pymongo.server_api import ServerApi

def create_app():
    app = Flask(__name__)

    uri = "mongodb+srv://temp_user:1234@stories.detzj4q.mongodb.net/?retryWrites=true&w=majority&appName=Stories"
    client = MongoClient(uri, server_api=ServerApi('1'))

    with app.app_context():
        # Try to connect and ping MongoDB when the app starts
        try:
            client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(e)
    
    @app.route('/')
    def home():
        return 'Hello, World!'

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
