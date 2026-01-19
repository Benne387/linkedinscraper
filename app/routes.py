from flask import Blueprint, request, jsonify, render_template, current_app
from app.scraper import scrape_profile_logic, login_to_linkedin, save_manual_cookies
from datetime import datetime

bp = Blueprint('main', __name__)

@bp.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@bp.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})

@bp.route('/scrape', methods=['POST'])
def scrape():
    data = request.get_json(silent=True)
    
    # Handle both JSON and Form data (if extended later)
    if not data:
        return jsonify({"status": "error", "error": "Invalid JSON"}), 400
        
    url = data.get('url')
    if not url:
        return jsonify({"status": "error", "error": "URL required"}), 400
    
    # Get sessionId 
    session_id = data.get('session_id', 'default_user')
    
    result = scrape_profile_logic(url, session_id=session_id)
    
    status_code = 200
    if result.get("status") == "error":
        status_code = 500
        
    return jsonify(result), status_code

@bp.route('/scrape/batch', methods=['POST'])
def scrape_batch():
    data = request.get_json(silent=True) or {}
    urls = data.get('urls', [])
    
    if not urls:
        return jsonify({"status": "error", "error": "URLs required"}), 400
        
    results = []
    for url in urls:
        results.append(scrape_profile_logic(url))
        
    return jsonify({
        "status": "success",
        "total": len(urls),
        "results": results
    })

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"status": "error", "message": "Email and password required"}), 400
        
    
    session_id = data.get('session_id', 'default_user')
    result = login_to_linkedin(email, password, session_id)
    return jsonify(result)

@bp.route('/cookies', methods=['POST'])
def upload_cookies():
    data = request.get_json(silent=True) or {}
    cookies = data.get('cookies') # text string
    
    if not cookies:
        return jsonify({"status": "error", "message": "Cookies JSON required"}), 400
        
    session_id = data.get('session_id', 'default_user')
    result = save_manual_cookies(cookies, session_id)
    return jsonify(result)
