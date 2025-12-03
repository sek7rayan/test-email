from flask import Flask, request, render_template_string
import datetime
import os
import base64

app = Flask(__name__)

# Fichier de logs
LOG_FILE = "spy_pixel_logs.txt"

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>🔍 Email Tracker - Render</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #4361ee 0%, #3a0ca3 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
        }
        .card {
            padding: 30px;
            border-bottom: 1px solid #eee;
        }
        .url-display {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            border: 2px dashed #4361ee;
            font-family: 'Courier New', monospace;
            font-size: 1.1em;
            word-break: break-all;
        }
        .code-block {
            background: #1e1e1e;
            color: #f8f8f8;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            font-family: 'Courier New', monospace;
            overflow-x: auto;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        .stat-box {
            background: #f0f7ff;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            border: 1px solid #d0e3ff;
        }
        .stat-box h3 {
            color: #4361ee;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .logs-container {
            background: #1a1a1a;
            color: #00ff88;
            padding: 25px;
            border-radius: 10px;
            margin: 30px 0;
            font-family: 'Consolas', monospace;
            max-height: 500px;
            overflow-y: auto;
        }
        .log-entry {
            padding: 8px 0;
            border-bottom: 1px solid #333;
        }
        .log-entry.real { border-left: 3px solid #00ff88; padding-left: 10px; }
        .log-entry.proxy { border-left: 3px solid #ff6b6b; padding-left: 10px; }
        .timestamp { color: #888; }
        .ip { color: #4cc9f0; font-weight: bold; }
        .ip.real { color: #00ff88; }
        .campaign { color: #f72585; }
        .ua { color: #f8961e; }
        .proxy-badge {
            background: #ff6b6b;
            color: white;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 0.8em;
            margin-left: 10px;
        }
        .btn {
            background: #4361ee;
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 50px;
            font-size: 1em;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 10px;
            text-decoration: none;
            transition: all 0.3s;
        }
        .btn:hover {
            background: #3a0ca3;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        .btn-copy {
            background: #2b9348;
        }
        .btn-copy:hover {
            background: #1b7a32;
        }
        .instructions {
            background: #e9f7ff;
            padding: 25px;
            border-radius: 10px;
            margin: 30px 0;
        }
        .step {
            display: flex;
            align-items: flex-start;
            gap: 15px;
            margin: 20px 0;
        }
        .step-number {
            background: #4361ee;
            color: white;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            font-weight: bold;
        }
        @media (max-width: 768px) {
            .container { margin: 10px; }
            .header { padding: 25px; }
            .header h1 { font-size: 1.8em; }
        }
        .filter-buttons {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        .filter-btn {
            background: #666;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 20px;
            cursor: pointer;
        }
        .filter-btn.active {
            background: #4361ee;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📧 <span>Email Tracker</span> <small>by Render</small></h1>
            <p>Trackez l'ouverture de vos emails en temps réel</p>
        </div>

        <div class="card">
            <h2>🎯 Votre URL de Tracking</h2>
            <div class="url-display" id="pixelUrl">
                {{ pixel_url }}/[votre_campagne]
            </div>
            <button class="btn btn-copy" onclick="copyUrl()">
                📋 Copier l'URL
            </button>
            <button class="btn" onclick="testPixel()">
                🧪 Tester le pixel
            </button>
            <a href="/debug" class="btn" style="background: #666;">
                🔧 Debug Headers
            </a>
        </div>

        <div class="stats">
            <div class="stat-box">
                <h3>{{ total_opens }}</h3>
                <p>📨 Ouvertures totales</p>
            </div>
            <div class="stat-box">
                <h3>{{ real_opens }}</h3>
                <p>👤 Ouvertures réelles</p>
            </div>
            <div class="stat-box">
                <h3>{{ campaigns_count }}</h3>
                <p>🏷️ Campagnes</p>
            </div>
            <div class="stat-box">
                <h3>{{ last_24h }}</h3>
                <p>🕐 24 dernières heures</p>
            </div>
        </div>

        <div class="card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h2>📊 Logs en direct</h2>
                <div class="filter-buttons">
                    <button class="filter-btn active" onclick="filterLogs('all')">Tous</button>
                    <button class="filter-btn" onclick="filterLogs('real')">Réels</button>
                    <button class="filter-btn" onclick="filterLogs('proxy')">Proxys</button>
                </div>
                <button class="btn" onclick="refreshLogs()">
                    🔄 Actualiser
                </button>
            </div>
            
            <div class="logs-container" id="logsContainer">
                {% if logs_data %}
                    {% for log in logs_data %}
                    <div class="log-entry {{ 'real' if log.is_real else 'proxy' }}" data-type="{{ 'real' if log.is_real else 'proxy' }}">
                        <span class="timestamp">[{{ log.timestamp }}]</span>
                        <span class="ip {{ 'real' if log.is_real else '' }}">
                            {{ log.ip }}
                            {% if not log.is_real %}
                            <span class="proxy-badge">Proxy</span>
                            {% endif %}
                        </span>
                        {% if log.campaign %}
                        <span class="campaign"> | {{ log.campaign }}</span>
                        {% endif %}
                        <span class="ua"> | {{ log.ua }}</span>
                    </div>
                    {% endfor %}
                {% else %}
                    <p>En attente de la première ouverture...</p>
                {% endif %}
            </div>
        </div>

        <div class="instructions">
            <h2>🚀 Comment utiliser</h2>
            
            <div class="step">
                <div class="step-number">1</div>
                <div>
                    <h3>Copiez votre URL de pixel</h3>
                    <p>Ajoutez un nom de campagne à la fin : <code>{{ pixel_url }}/newsletter_mars</code></p>
                </div>
            </div>

            <div class="step">
                <div class="step-number">2</div>
                <div>
                    <h3>Insérez dans vos emails</h3>
                    <div class="code-block">
&lt;img src="{{ pixel_url }}/nom_campagne" 
     width="1" height="1" 
     style="display:none; border:none;" 
     alt="tracker"&gt;
                    </div>
                </div>
            </div>

            <div class="step">
                <div class="step-number">3</div>
                <div>
                    <h3>Surveillez les ouvertures</h3>
                    <p>Les données apparaîtront ici automatiquement quand l'email sera ouvert</p>
                    <p><small>⚠️ Note : Gmail utilise un proxy, vous verrez "Proxy" sur les ouvertures Gmail</small></p>
                </div>
            </div>
        </div>

        <div class="card" style="text-align: center; color: #666; font-size: 0.9em;">
            <p>🛡️ Ce tracker est à des fins éducatives uniquement. Respectez toujours la vie privée.</p>
            <p>💡 <strong>IP Réelle</strong> = Ouverture directe • <strong>Proxy</strong> = Gmail/Client email</p>
            <p>Déployé sur <strong>Render</strong> • <a href="https://render.com" style="color: #4361ee;">render.com</a></p>
        </div>
    </div>

    <script>
        function copyUrl() {
            const url = "{{ pixel_url }}";
            navigator.clipboard.writeText(url);
            alert('✅ URL copiée : ' + url);
        }
        
        function testPixel() {
            const testUrl = "{{ pixel_url }}/test_" + Date.now();
            fetch(testUrl)
                .then(() => {
                    alert('✅ Pixel testé ! Rafraîchissez la page pour voir le log.');
                    setTimeout(() => location.reload(), 1000);
                })
                .catch(err => alert('❌ Erreur : ' + err));
        }
        
        function refreshLogs() {
            location.reload();
        }
        
        function filterLogs(type) {
            const buttons = document.querySelectorAll('.filter-btn');
            buttons.forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            const logs = document.querySelectorAll('.log-entry');
            logs.forEach(log => {
                if (type === 'all') {
                    log.style.display = 'block';
                } else {
                    if (log.dataset.type === type) {
                        log.style.display = 'block';
                    } else {
                        log.style.display = 'none';
                    }
                }
            });
        }
        
        // Auto-refresh toutes les 30 secondes
        setTimeout(refreshLogs, 30000);
    </script>
</body>
</html>
'''

def parse_logs():
    """Parse les logs pour les statistiques"""
    if not os.path.exists(LOG_FILE):
        return [], 0, 0, 0, 0, 0
    
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    logs_data = []
    ips = set()
    campaigns = set()
    last_24h_count = 0
    real_opens_count = 0
    
    for line in reversed(lines[-200:]):  # Derniers 200 logs
        try:
            parts = line.strip().split(' | ')
            if len(parts) < 3:
                continue
                
            timestamp_str = parts[0][1:-1]  # Enlever les crochets
            ip_part = parts[1]
            
            # Extraire l'IP
            if 'IP: ' in ip_part:
                ip = ip_part.replace('IP: ', '').strip()
            else:
                ip = ip_part.strip()
            
            # Détecter si c'est une ouverture réelle (pas proxy)
            is_real = True
            if 'Proxy: Gmail' in line or 'Proxy: Yes' in line:
                is_real = False
            else:
                real_opens_count += 1
            
            campaign = None
            ua = parts[2].replace('UA: ', '') if len(parts) > 2 else 'Unknown'
            
            # Chercher campagne
            for part in parts:
                if 'Campaign: ' in part:
                    campaign = part.split('Campaign: ')[1].strip()
                    campaigns.add(campaign)
                    break
            
            # Convertir timestamp
            try:
                timestamp = datetime.datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                
                # Compter dernières 24h
                time_diff = datetime.datetime.now() - timestamp
                if time_diff.total_seconds() < 86400:
                    last_24h_count += 1
            except:
                timestamp = datetime.datetime.now()
            
            logs_data.append({
                'timestamp': timestamp_str,
                'ip': ip,
                'campaign': campaign,
                'ua': ua[:60] + '...' if len(ua) > 60 else ua,
                'is_real': is_real
            })
            
            ips.add(ip)
            
        except Exception as e:
            print(f"Error parsing log line: {e}")
            continue
    
    return logs_data, len(lines), real_opens_count, len(campaigns), last_24h_count

@app.route('/')
def home():
    base_url = request.url_root.rstrip('/')
    pixel_url = f"{base_url}/pixel"
    
    logs_data, total, real_opens, campaigns, last_24h = parse_logs()
    
    return render_template_string(HTML_TEMPLATE,
        pixel_url=pixel_url,
        logs_data=logs_data,
        total_opens=total,
        real_opens=real_opens,
        campaigns_count=campaigns,
        last_24h=last_24h
    )

@app.route('/pixel')
@app.route('/pixel/<campaign>')
def track_pixel(campaign=None):
    """Route principale pour tracker les ouvertures d'emails"""
    
    # 1. Détection AVANCÉE de l'IP réelle
    ip = request.remote_addr  # IP par défaut
    
    # Liste des headers à vérifier (dans l'ordre de priorité)
    ip_headers = [
        'X-Client-IP',
        'X-Real-IP', 
        'X-Forwarded-For',
        'X-Forwarded',
        'Forwarded-For',
        'Forwarded',
        'CF-Connecting-IP',  # Cloudflare
        'True-Client-IP',    # Akamai
    ]
    
    for header in ip_headers:
        if header in request.headers:
            # Prendre la première IP de la liste
            ips = request.headers[header].split(',')
            ip = ips[0].strip()
            print(f"Found IP in {header}: {ip}")
            break
    
    # 2. Détecter si c'est un proxy Gmail
    user_agent = request.headers.get('User-Agent', 'Unknown')
    is_gmail_proxy = any([
        'GoogleImageProxy' in user_agent,
        'googleusercontent' in user_agent,
        'Google' in user_agent and 'Image' in user_agent
    ])
    
    # 3. Information sur le proxy
    proxy_info = ""
    if is_gmail_proxy:
        proxy_info = " | Proxy: Gmail"
    elif 'X-Forwarded-For' in request.headers:
        proxy_info = " | Proxy: Yes"
    
    # 4. Obtenir d'autres informations
    referer = request.headers.get('Referer', 'Direct')
    accept_language = request.headers.get('Accept-Language', '')
    
    # 5. Format du log amélioré
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    log_entry = f"[{timestamp}] | IP: {ip}"
    log_entry += proxy_info
    log_entry += f" | UA: {user_agent}"
    if campaign:
        log_entry += f" | Campaign: {campaign}"
    
    # 6. Debug info (pour les logs Render)
    debug_info = f"""
    📡 PIXEL TRACKED:
    - Timestamp: {timestamp}
    - Final IP: {ip}
    - User-Agent: {user_agent[:100]}
    - Campaign: {campaign}
    - Is Gmail Proxy: {is_gmail_proxy}
    - Referer: {referer}
    """
    print(debug_info)
    
    # 7. Sauvegarder
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_entry + '\n')
    
    # 8. Retourner le pixel 1x1 transparent
    pixel_data = base64.b64decode(
        'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII='
    )
    
    response_headers = {
        'Content-Type': 'image/png',
        'Content-Length': str(len(pixel_data)),
        'Cache-Control': 'no-store, no-cache, must-revalidate, max-age=0',
        'Pragma': 'no-cache',
        'Expires': '0',
        'Access-Control-Allow-Origin': '*',
        'X-Content-Type-Options': 'nosniff',
    }
    
    return pixel_data, 200, response_headers

@app.route('/debug')
def debug_headers():
    """Page de debug pour voir tous les headers"""
    headers = []
    for key, value in request.headers:
        headers.append(f"{key}: {value}")
    
    html = f"""
    <html>
    <style>
        body {{ font-family: monospace; padding: 20px; background: #1a1a1a; color: #0f0; }}
        h1 {{ color: #fff; }}
        .header {{ background: #333; padding: 10px; margin: 5px 0; }}
        .ip {{ color: #4cc9f0; font-weight: bold; }}
    </style>
    <body>
        <h1>🔧 Debug Headers</h1>
        <p>Remote Addr: <span class="ip">{request.remote_addr}</span></p>
        <p>URL: {request.url}</p>
        <hr>
        <h2>Headers reçus :</h2>
        {"".join([f'<div class="header">{h}</div>' for h in headers])}
        <hr>
        <h2>Test rapide :</h2>
        <button onclick="testPixel()">Test Pixel</button>
        <button onclick="location.href='/'">Retour</button>
        <script>
            function testPixel() {{
                fetch('/pixel/debug_test_' + Date.now())
                    .then(() => alert('Pixel testé !'))
                    .catch(e => alert('Erreur: ' + e));
            }}
        </script>
    </body>
    </html>
    """
    return html

@app.route('/clear', methods=['POST'])
def clear_logs():
    """Effacer les logs (protégé)"""
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
    return "Logs cleared", 200

@app.route('/api/logs')
def api_logs():
    """API pour récupérer les logs en JSON"""
    logs_data, total, real_opens, campaigns, last_24h = parse_logs()
    return {
        'total': total,
        'real_opens': real_opens,
        'campaigns': campaigns,
        'last_24h': last_24h,
        'logs': logs_data
    }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)