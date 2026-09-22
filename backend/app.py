import sys
from pathlib import Path

# Add project root directory to Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from flask import Flask, render_template, jsonify, request
from config.settings import Config
from database.db import init_db
from backend.routes.auth_routes import auth_bp
from backend.routes.classification_routes import classification_bp
from backend.routes.route_routes import route_bp
from backend.routes.dashboard_routes import dashboard_bp
from backend.routes.admin_routes import admin_bp
from backend.routes.report_routes import report_bp

def create_app(config_class=Config):
    app = Flask(__name__, 
                template_folder='../templates', 
                static_folder='../static')
    
    # Load configuration
    app.config.from_object(config_class)

    # Initialize Supabase database teardown handler
    init_db(app)

    # Register API Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(classification_bp)
    app.register_blueprint(route_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(report_bp)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/classify')
    def classification_page():
        return render_template('classification.html')

    @app.route('/routes')
    def routes_page():
        return render_template('routes.html')

    @app.route('/dashboard')
    def dashboard_page():
        return render_template('dashboard.html')

    @app.route('/admin')
    def admin_page():
        return render_template('admin.html')

    @app.errorhandler(404)
    def not_found_error(error):
        if request.path.startswith('/api/'):
            return jsonify({'success': False, 'message': 'API endpoint not found'}), 404
        return render_template('index.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        if request.path.startswith('/api/'):
            return jsonify({'success': False, 'message': 'Internal server error'}), 500
        return "500 Internal Server Error", 500

    # Limit uploads to 5MB
    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

    return app

app = create_app()

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting development server on 0.0.0.0:{port}. Use wsgi.py for production.")
    app.run(host='0.0.0.0', port=port, debug=app.config.get('DEBUG', False))
