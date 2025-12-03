from flask import Flask, request, send_file, render_template_string
import datetime
import os
import base64

app = Flask(__name__)

LOG_FILE = "spy_pixel_logs.txt"

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Pixel Tracker</title>
    <style>
        body { font-family: Arial; max-width: 1000px; margin: 0 auto; padding: 20px; }
        .header { background: #4a6fa5; color: white; padding: 20px; border-radius: 10px; }
        .url-box { background: #f0f0f0; padding: 15px; margin: 20px 0; border-radius: 5px; }
        .logs { background: #222; color: #0f0; padding: 15px; border-radius: 5px; font-family: monospace; }
    </style>
</head>
<body>
    <div class="header">
        <h1>📡 Pixel Tracker</h1>
        <p>Votre URL de pixel : <strong>{{ pixel_url }}</strong></p>
    </div>
    
    <h2>Comment utiliser :</h2>
    <p>Ajoutez ce code dans vos emails :</p>
    <div class="url-box">
        <code>&lt;img src="{{ pixel_url }}/NOM_CAMPAGNE" width="1" height="1" style="display:none"&gt;</code>
    </div>
    
    <h2>📊 Logs :</h2>
    <div class="logs">
        {% if logs %}
        <pre>{{ logs }}</pre>
        {% else %}
        <p>En attente de données...</p>
        {% endif %}
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    base_url = request.url_root.rstrip('/')
    pixel_url = f"{base_url}/pixel"
    
    logs = ""
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            logs = f.read()
    
    return render_template_string(HTML_TEMPLATE, pixel_url=pixel_url, logs=logs)

@app.route('/pixel')
@app.route('/pixel/<campaign>')
def track_pixel(campaign=None):
    # Get data
    user_agent = request.headers.get('User-Agent', 'Unknown')
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Create log entry
    log_entry = f"[{timestamp}] IP: {ip} | UA: {user_agent[:80]}"
    if campaign:
        log_entry += f" | Campaign: {campaign}"
    
    # Save to file
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_entry + '\n')
    
    # Print to console (for Railway logs)
    print(f"Pixel tracked: {log_entry}")
    
    # Return 1x1 transparent PNG
    pixel = base64.b64decode(
        'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII='
    )
    
    return pixel, 200, {
        'Content-Type': 'image/png',
        'Cache-Control': 'no-store'
    }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)