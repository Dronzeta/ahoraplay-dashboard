import json
import urllib.request
import datetime
import os

# Configuración de Identidad
# Usamos el Token del entorno (Secret) si existe, sino el manual
AUTH_TOKEN = os.getenv("METRICOOL_TOKEN", "HIPVBFNGOGNLFVQQXVQEKDOKQNJMZLZCKRFDULSYVFMAFMIYUMJKOYZZNIHUCDEZ")
BLOG_ID = "6130804"

def fetch_metricool_data(network, endpoint="posts"):
    today = datetime.datetime.now()
    seven_days_ago = today - datetime.timedelta(days=7)
    
    date_from = seven_days_ago.strftime("%Y-%m-%dT00:00:00")
    date_to = today.strftime("%Y-%m-%dT23:59:59")
    
    url = f"https://api.metricool.com/api/v1/analytics/{network}/{endpoint}?blogId={BLOG_ID}&from={date_from}&to={date_to}"
    
    req = urllib.request.Request(url)
    req.add_header("X-Mc-Auth", AUTH_TOKEN)
    
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Error fetching {network} {endpoint}: {e}")
        return None

def process_data():
    print("🚀 Iniciando extracción de datos avanzados...")
    
    # Redes a procesar
    networks = ['youtube', 'tiktok', 'instagram', 'facebook', 'twitter']
    raw_data = {}
    
    for net in networks:
        print(f"📦 Procesando {net}...")
        raw_data[net] = fetch_metricool_data(net)
        
    # Estructura del Dashboard
    db_data = {
        "last_update": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "summary": {
            "total_followers": 425800, # Valor base para simulación
            "avg_engagement": 0,
            "networks": {}
        },
        "details": {}
    }
    
    # Procesamiento Específico por Red
    for net, data in raw_data.items():
        if not data or 'data' not in data:
            continue
            
        items = data['data']
        
        if net == 'youtube':
            shorts = [v for v in items if v.get('videoType') == 'SHORT']
            db_data['details']['youtube'] = {
                "total_views": sum(v.get('views', 0) for v in items),
                "watch_time": sum(v.get('watchMinutes', 0) for v in items),
                "shorts": sorted(shorts, key=lambda x: x.get('views', 0), reverse=True)[:5],
                "traffic_sources": {"Búsqueda": 45, "Sugeridos": 30, "Directo": 25}
            }
            
        elif net == 'tiktok':
            db_data['details']['tiktok'] = {
                "total_views": sum(v.get('viewCount', 0) for v in items),
                "avg_completion": (sum(v.get('fullVideoWatchedRate', 0) for v in items) / len(items)) if items else 0,
                "top_posts": sorted(items, key=lambda x: x.get('viewCount', 0), reverse=True)[:5]
            }
            
        elif net == 'instagram':
            db_data['details']['instagram'] = {
                "reach": sum(p.get('reach', 0) for p in items),
                "interactions": sum(p.get('interactions', 0) for p in items),
                "likes": sum(p.get('likes', 0) for p in items)
            }

        elif net == 'twitter':
            db_data['details']['twitter'] = {
                "impressions": sum(p.get('impressions', 0) for p in items),
                "retweets": sum(p.get('retweets', 0) or p.get('shares', 0) for p in items),
                "top_posts": sorted(items, key=lambda x: x.get('interactions', 0), reverse=True)[:5]
            }

    # Guardar para el Dashboard - USAMOS RUTA RELATIVA PARA GITHUB
    output_file = 'metricool_data.json'
    with open(output_file, 'w') as f:
        json.dump(db_data, f, indent=4)
        
    print(f"✅ {output_file} actualizado correctamente en la carpeta raíz.")

if __name__ == "__main__":
    process_data()
