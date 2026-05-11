import json
import requests
import datetime
import os

# CONFIGURACIÓN
AUTH_TOKEN = "HIPVBFNGOGNLFVQQXVQEKDOKQNJMZLZCKRFDULSYVFMAFMIYUMJKOYZZNIHUCDEZ"
BLOG_ID = "6130804"

def fetch_metricool_data(network):
    today = datetime.datetime.now()
    month_ago = today - datetime.timedelta(days=30)
    
    # URL CLON n8n: La red va como parámetro 'network', no en la ruta
    url = "https://app.metricool.com/api/v1/analytics/posts"
    
    params = {
        "blogid": BLOG_ID,
        "network": network,
        "from": month_ago.strftime("%Y-%m-%d"),
        "to": today.strftime("%Y-%m-%d")
    }
    
    headers = {
        "X-Mc-Auth": AUTH_TOKEN,
        "Accept": "application/json"
    }
    
    print(f"📡 Consultando {network} (Modo Clon n8n)...")
    
    try:
        # Intentamos la ruta que n8n usa con parámetros
        response = requests.get(url, params=params, headers=headers)
        
        # Si esta falla, intentamos la ruta de métricas de red (analytics/{network})
        if response.status_code != 200:
            print(f"⚠️ Falló modo n8n. Probando ruta base de analítica...")
            url_alt = f"https://app.metricool.com/api/v1/analytics/{network}"
            response = requests.get(url_alt, params=params, headers=headers)

        if response.status_code == 200:
            data = response.json().get('data', [])
            print(f"✅ {network}: {len(data) if isinstance(data, list) else '1'} registros.")
            return data
        else:
            print(f"❌ {network}: Error {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error en {network}: {e}")
        return []

def process_data():
    networks = ['youtube', 'tiktok', 'instagram', 'twitter']
    db_data = {
        "last_update": datetime.datetime.now().strftime("%d %b, %H:%M"),
        "details": {}
    }
    
    for net in networks:
        data = fetch_metricool_data(net)
        if not data: continue
        
        # Procesamiento unificado
        if isinstance(data, list):
            vistas = sum(int(v.get('views', 0) or v.get('viewCount', 0) or v.get('impressions', 0)) for v in data)
            posts = sorted([{"title": v.get('title') or v.get('text') or "Post", "val": f"{v.get('views', 0) or v.get('viewCount', 0)} v"} for v in data], key=lambda x: int(x['val'].split()[0]), reverse=True)[:6]
        else:
            # Caso de respuesta dict
            vistas = data.get('views', 0) or data.get('viewCount', 0) or 0
            posts = []

        db_data['details'][net] = {
            "total_views": vistas,
            "top_posts": posts
        }

    with open('metricool_data.js', 'w', encoding='utf-8') as f:
        f.write(f"window.metricoolData = {json.dumps(db_data, indent=4, ensure_ascii=False)};")
    
    print("🚀 Dashboard actualizado.")

if __name__ == "__main__":
    process_data()
