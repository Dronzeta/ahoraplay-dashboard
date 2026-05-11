import json
import requests
import datetime
import os

# CONFIGURACIÓN (Basada en documentación oficial)
AUTH_TOKEN = "HIPVBFNGOGNLFVQQXVQEKDOKQNJMZLZCKRFDULSYVFMAFMIYUMJKOYZZNIHUCDEZ"
BLOG_ID = "6130804"

def fetch_metricool_data(network):
    today = datetime.datetime.now()
    month_ago = today - datetime.timedelta(days=30)
    
    # URL DOCUMENTADA: https://app.metricool.com/api/v1/analytics/posts/{network}
    url = f"https://app.metricool.com/api/v1/analytics/posts/{network}"
    
    # LA CLAVE: El formato de fecha debe ser EXACTO según la doc: YYYY-MM-DDTHH:mm:ss
    params = {
        "blogId": BLOG_ID, # Probamos con I mayúscula como dice la doc principal
        "blogid": BLOG_ID, # Enviamos también en minúscula por seguridad
        "from": month_ago.strftime("%Y-%m-%dT00:00:00"),
        "to": today.strftime("%Y-%m-%dT23:59:59")
    }
    
    headers = {
        "X-Mc-Auth": AUTH_TOKEN,
        "Accept": "application/json"
    }
    
    print(f"🔍 Consultando {network} (Doc Mode)...")
    
    try:
        response = requests.get(url, params=params, headers=headers)
        
        # Si da 404 con /posts/{network}, probamos la ruta base /{network}
        if response.status_code == 404:
            print(f"⚠️ {network}/posts no encontrado. Probando analytics/{network}...")
            url_alt = f"https://app.metricool.com/api/v1/analytics/{network}"
            response = requests.get(url_alt, params=params, headers=headers)

        if response.status_code == 200:
            res_json = response.json()
            # La doc dice que los datos pueden venir en 'data' o directamente
            data = res_json.get('data', res_json)
            if not isinstance(data, list): data = [data] if data else []
            print(f"✅ {network}: {len(data)} registros obtenidos.")
            return data
        else:
            print(f"❌ {network}: Error {response.status_code} - {response.text[:100]}")
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
        
        # Procesamiento de métricas según el campo de la doc
        vistas = sum(int(v.get('views', 0) or v.get('viewCount', 0) or v.get('impressions', 0)) for v in data)
        posts = []
        for v in sorted(data, key=lambda x: int(x.get('views', 0) or x.get('viewCount', 0) or 0), reverse=True)[:6]:
            titulo = v.get('title') or v.get('text') or "Post"
            val = v.get('views') or v.get('viewCount') or 0
            posts.append({"title": titulo, "val": f"{val} v"})
        
        db_data['details'][net] = {
            "total_views": vistas,
            "top_posts": posts
        }

    with open('metricool_data.js', 'w', encoding='utf-8') as f:
        f.write(f"window.metricoolData = {json.dumps(db_data, indent=4, ensure_ascii=False)};")
    
    print("🚀 Dashboard actualizado con parámetros de la documentación oficial.")

if __name__ == "__main__":
    process_data()
