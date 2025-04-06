from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import uuid
import datetime

# Import your existing chatbot code
from main import app as chatbot_app, save_conversation_to_file  # Change to your actual file name

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Store conversation threads
conversation_threads = {}

# Route to serve the index.html file
@app.route('/')
def serve_index():
    # Serves index.html from the same directory as api.py
    return send_from_directory('.', 'index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        message = data.get('message', '')
        thread_id = data.get('thread_id', str(uuid.uuid4()))

        # Prepare input for your LangGraph app
        inputs = {"messages": [{"type": "human", "content": message}]}
        config = {"configurable": {"thread_id": thread_id}}

        # Get response from your chatbot
        result = chatbot_app.invoke(inputs, config=config)

        # Extract assistant's response
        assistant_response = result["messages"][-1].content

        # Store in conversation history
        if thread_id not in conversation_threads:
            conversation_threads[thread_id] = []

        conversation_threads[thread_id].append({"role": "user", "content": message})
        conversation_threads[thread_id].append({"role": "assistant", "content": assistant_response})

        return jsonify({
            "response": assistant_response,
            "thread_id": thread_id
        })

    except Exception as e:
        return jsonify({
            "error": str(e),
            "response": "حدث خطأ أثناء معالجة طلبك."
        }), 500

@app.route('/api/save', methods=['POST'])
def save_conversation():
    try:
        data = request.json
        thread_id = data.get('thread_id')

        if not thread_id or thread_id not in conversation_threads:
            return jsonify({"success": False, "error": "Thread ID not found"}), 404

        # Get conversation history
        conversation_history = conversation_threads[thread_id]

        # Save to file using your existing function
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"conversation_{timestamp}.txt"

        success = save_conversation_to_file(conversation_history, filename)

        return jsonify({"success": success, "filename": filename})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)