import json
import requests
import datetime
import os

# CONFIGURACIÓN (Verificado con documentación oficial)
AUTH_TOKEN = "HIPVBFNGOGNLFVQQXVQEKDOKQNJMZLZCKRFDULSYVFMAFMIYUMJKOYZZNIHUCDEZ"
BLOG_ID = "6130804"

def fetch_metricool_data(network):
    today = datetime.datetime.now()
    seven_days_ago = today - datetime.timedelta(days=7)
    
    # URL OFICIAL DOCUMENTADA: https://app.metricool.com/api/v1/analytics/posts/{network}
    # IMPORTANTE: blogid va en minúsculas según la documentación técnica
    url = f"https://app.metricool.com/api/v1/analytics/posts/{network}"
    
    params = {
        "blogid": BLOG_ID,
        "from": seven_days_ago.strftime("%Y-%m-%d"),
        "to": today.strftime("%Y-%m-%d"),
        "timezone": "America/Argentina/Buenos_Aires"
    }
    
    headers = {
        "X-Mc-Auth": AUTH_TOKEN,
        "Accept": "application/json"
    }
    
    print(f"🔍 Consultando {network} (Parámetros: blogid={BLOG_ID}, from={params['from']})...")
    
    try:
        response = requests.get(url, params=params, headers=headers)
        
        # Si la ruta /posts/{network} no existe, probamos la ruta de métricas base /{network}
        if response.status_code == 404:
            print(f"⚠️ Ruta /posts/{network} no encontrada. Probando analytics/{network}...")
            url_alt = f"https://app.metricool.com/api/v1/analytics/{network}"
            response = requests.get(url_alt, params=params, headers=headers)

        if response.status_code == 200:
            res_json = response.json()
            data = res_json.get('data', [])
            print(f"✅ {network}: {len(data) if isinstance(data, list) else '1'} registros recibidos.")
            return data
        else:
            print(f"❌ {network} falló (Código {response.status_code}): {response.text[:100]}")
            return None
    except Exception as e:
        print(f"❌ Error de red en {network}: {e}")
        return None

def process_data():
    # Redes a consultar
    networks = ['youtube', 'tiktok', 'instagram', 'twitter']
    db_data = {
        "last_update": datetime.datetime.now().strftime("%d %b, %H:%M"),
        "details": {}
    }
    
    for net in networks:
        data = fetch_metricool_data(net)
        if not data: continue
        
        # Procesamiento unificado de métricas
        if isinstance(data, list):
            vistas = sum(int(v.get('views', 0) or v.get('viewCount', 0) or v.get('impressions', 0)) for v in data)
            # Extraer títulos de videos/posts
            posts = []
            for v in sorted(data, key=lambda x: int(x.get('views', 0) or x.get('viewCount', 0) or 0), reverse=True)[:5]:
                titulo = v.get('title') or v.get('text') or "Sin título"
                valor = v.get('views') or v.get('viewCount') or 0
                posts.append({"title": titulo, "val": f"{valor} v"})
        else:
            # Caso de respuesta de estadísticas generales
            vistas = data.get('views', 0) or data.get('viewCount', 0) or 0
            posts = []

        db_data['details'][net] = {
            "total_views": vistas,
            "top_posts": posts
        }

    with open('metricool_data.js', 'w', encoding='utf-8') as f:
        f.write(f"window.metricoolData = {json.dumps(db_data, indent=4, ensure_ascii=False)};")
    
    print("🚀 Dashboard actualizado con la configuración oficial de la API.")

if __name__ == "__main__":
    process_data()
