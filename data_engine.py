import json
import requests
import datetime
import os

# CONFIGURACIÓN
AUTH_TOKEN = "HIPVBFNGOGNLFVQQXVQEKDOKQNJMZLZCKRFDULSYVFMAFMIYUMJKOYZZNIHUCDEZ"
BLOG_ID = "6130804"

def fetch_metricool_data(network):
    today = datetime.datetime.now()
    seven_days_ago = today - datetime.timedelta(days=7)
    
    # URL V2: Esta es la que Metricool usa para sus integraciones modernas
    # Nota: Usamos app.metricool.com porque es el host que GitHub sí resuelve
    url = f"https://app.metricool.com/api/v1/analytics/{network}/posts"
    
    params = {
        "blogId": BLOG_ID,
        "from": seven_days_ago.strftime("%Y-%m-%dT00:00:00"),
        "to": today.strftime("%Y-%m-%dT23:59:59")
    }
    
    headers = {
        "X-Mc-Auth": AUTH_TOKEN,
        "Accept": "application/json"
    }
    
    print(f"🔍 Consultando {network}...")
    
    try:
        response = requests.get(url, params=params, headers=headers)
        
        # Si da 404, probamos la ruta de "stats" que es más robusta
        if response.status_code == 404:
            print(f"⚠️ {network}/posts dio 404. Probando ruta de estadísticas...")
            url_alt = f"https://app.metricool.com/api/v1/analytics/{network}"
            response = requests.get(url_alt, params=params, headers=headers)

        if response.status_code == 200:
            res_json = response.json()
            data = res_json.get('data', [])
            # Si data es un dict (en stats), lo metemos en una lista
            if isinstance(data, dict): data = [data]
            print(f"✅ {network}: {len(data)} registros obtenidos.")
            return data
        else:
            print(f"❌ {network} falló con código {response.status_code}")
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
        
        # Procesamiento inteligente de métricas
        vistas = sum(int(v.get('views', 0) or v.get('viewCount', 0) or v.get('impressions', 0)) for v in data)
        
        db_data['details'][net] = {
            "total_views": vistas,
            "top_posts": sorted([{"title": v.get('title') or v.get('text') or "Post", "val": f"{v.get('views', 0) or v.get('viewCount', 0)} v"} for v in data], key=lambda x: int(x['val'].split()[0]), reverse=True)[:5]
        }
        
    with open('metricool_data.js', 'w', encoding='utf-8') as f:
        f.write(f"window.metricoolData = {json.dumps(db_data, indent=4, ensure_ascii=False)};")
    
    print("🚀 Dashboard actualizado.")

if __name__ == "__main__":
    process_data()
