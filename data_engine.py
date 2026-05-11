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
    
    # CAMBIO DE DOMINIO: api.metricool.com en lugar de app.metricool.com
    url = f"https://api.metricool.com/api/v1/analytics/{network}/posts"
    
    params = {
        "blogId": BLOG_ID,
        "from": seven_days_ago.strftime("%Y-%m-%dT00:00:00"),
        "to": today.strftime("%Y-%m-%dT23:59:59")
    }
    
    headers = {
        "X-Mc-Auth": AUTH_TOKEN,
        "Accept": "application/json"
    }
    
    print(f"🔍 Consultando {network} en api.metricool.com...")
    
    try:
        # Probamos con el dominio API directamente
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code == 200:
            data = response.json().get('data', [])
            print(f"✅ {network}: {len(data)} registros.")
            return data
        else:
            print(f"❌ {network} falló (Código {response.status_code})")
            # Intento alternativo sin /posts
            url_alt = f"https://api.metricool.com/api/v1/analytics/{network}"
            res_alt = requests.get(url_alt, params=params, headers=headers)
            if res_alt.status_code == 200:
                print(f"✅ {network} (stats): Datos recibidos.")
                return res_alt.json().get('data', res_alt.json())
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
        data = fetch_metricool_data(net)
        if not data: continue
        
        # Procesamiento unificado
        if isinstance(data, list):
            vistas = sum(int(v.get('views', 0) or v.get('viewCount', 0) or v.get('impressions', 0)) for v in data)
            posts = sorted([{"title": v.get('title') or v.get('text') or "Post", "val": f"{v.get('views', 0) or v.get('viewCount', 0)} v"} for v in data], key=lambda x: int(x['val'].split()[0]), reverse=True)[:5]
        else:
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
