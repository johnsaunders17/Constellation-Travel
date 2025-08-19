import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from agent.app import app
    print("✅ Successfully imported Flask app")
except ImportError as e:
    print(f"❌ Import error: {e}")
    # Create a minimal fallback app
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/health')
    def health():
        return {'status': 'fallback', 'error': str(e)}
    
    @app.route('/')
    def home():
        return {'message': 'Fallback app running'}

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5001)))
