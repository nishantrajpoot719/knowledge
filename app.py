from flask import Flask, request, jsonify
from open_knowledge import Knowledge_Agent
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize the knowledge agent
knowledge_agent = Knowledge_Agent()

@app.route('/')
def home():
    return "Knowledge API is running!"

@app.route('/query', methods=['POST', 'GET'])
def process_query():
    try:
        data = request.get()
        user_query = data.get('query', '')
        
        if not user_query:
            return jsonify({"error": "No query provided"}), 400
        
        # Process the query
        response = knowledge_agent.process_user_query(user_query)
        
        return jsonify({
            "query": user_query,
            "response": response
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('FLASK_DEBUG', 'false').lower() == 'true')
