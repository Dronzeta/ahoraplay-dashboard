import json
import requests
import datetime
import os

# CONFIGURACIÓN
AUTH_TOKEN = "HIPVBFNGOGNLFVQQXVQEKDOKQNJMZLZCKRFDULSYVFMAFMIYUMJKOYZZNIHUCDEZ"
BLOG_ID = "6130804"

def fetch_metricool_stats(network):
    today = datetime.datetime.now()
    seven_days_ago = today - datetime.timedelta(days=7)
    
    # URL de ESTADÍSTICAS (Más estable que la de posts)
    url = f"https://app.metricool.com/api/v1/analytics/{network}"
    
    params = {
        "blogId": BLOG_ID,
        "from": seven_days_ago.strftime("%Y-%m-%dT00:00:00"),
        "to": today.strftime("%Y-%m-%dT23:59:59")
    }
    
    headers = {
        "X-Mc-Auth": AUTH_TOKEN,
        "Accept": "application/json"
    }
    
    print(f"🔍 Consultando estadísticas de {network}...")
    
    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            # En este endpoint, la data suele venir en un campo 'data' o directamente en la raíz
            res = data.get('data', data)
            print(f"✅ {network}: Datos recibidos.")
            return res
        else:
            print(f"❌ {network} falló (Código {response.status_code})")
            return None
    except Exception as e:
        print(f"❌ Error en {network}: {e}")
        return None

def process_data():
    networks = ['youtube', 'tiktok', 'instagram', 'twitter']
    db_data = {
        "last_update": datetime.datetime.now().strftime("%d %b, %H:%M"),
        "details": {}
    }
    
    for net in networks:
        data = fetch_metricool_stats(net)
        if not data: continue
        
        # Procesamiento de métricas de red
        if net == 'youtube':
            vistas = sum(v.get('views', 0) for v in data) if isinstance(data, list) else data.get('views', 0)
            db_data['details'][net] = {"total_views": vistas}
        elif net == 'tiktok':
            vistas = sum(v.get('viewCount', 0) for v in data) if isinstance(data, list) else data.get('viewCount', 0)
            db_data['details'][net] = {"total_views": vistas}
        else:
            db_data['details'][net] = {"total_views": 0}

    with open('metricool_data.js', 'w', encoding='utf-8') as f:
        f.write(f"window.metricoolData = {json.dumps(db_data, indent=4, ensure_ascii=False)};")
    
    print("🚀 Dashboard actualizado con estadísticas base.")

if __name__ == "__main__":
    process_data()
