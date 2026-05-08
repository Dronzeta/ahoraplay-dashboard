import json
import urllib.request
import datetime
import os

# CONFIGURACIÓN
AUTH_TOKEN = "HIPVBFNGOGNLFVQQXVQEKDOKQNJMZLZCKRFDULSYVFMAFMIYUMJKOYZZNIHUCDEZ"
BLOG_ID = "6130804"

def fetch_metricool_data(network):
    today = datetime.datetime.now()
    seven_days_ago = today - datetime.timedelta(days=7)
    date_from = seven_days_ago.strftime("%Y-%m-%dT00:00:00")
    date_to = today.strftime("%Y-%m-%dT23:59:59")
    
    # LISTA DE POSIBLES ENDPOINTS (Metricool es inconsistente)
    endpoints = [
        f"https://app.metricool.com/api/v1/analytics/{network}/posts?blogId={BLOG_ID}&from={date_from}&to={date_to}",
        f"https://app.metricool.com/api/v1/analytics/posts?network={network}&blogId={BLOG_ID}&from={date_from}&to={date_to}",
        f"https://api.metricool.com/api/v1/analytics/{network}?blogId={BLOG_ID}&from={date_from}&to={date_to}"
    ]
    
    for url in endpoints:
        print(f"🔍 Probando: {url[:60]}...")
        req = urllib.request.Request(url)
        req.add_header("X-Mc-Auth", AUTH_TOKEN)
        
        try:
            with urllib.request.urlopen(req) as response:
                res_json = json.loads(response.read().decode())
                data_list = res_json.get('data', [])
                if data_list:
                    print(f"✅ ¡ÉXITO en {network}! ({len(data_list)} registros)")
                    return data_list
                else:
                    # Si devuelve [] vacío, probamos el siguiente
                    print(f"⚠️ {network} respondió vacío en esta URL.")
        except Exception as e:
            print(f"❌ Falló esta ruta: {str(e)[:50]}")
            continue
            
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
        
        # Procesamiento genérico de vistas (funciona para casi todas)
        vistas = sum(v.get('views', 0) or v.get('viewCount', 0) or v.get('impressions', 0) for v in data)
        
        db_data['details'][net] = {
            "total_views": vistas,
            "top_posts": sorted([{"title": v.get('title') or v.get('text') or "Post", "val": f"{v.get('views', 0) or v.get('viewCount', 0)} v"} for v in data], key=lambda x: int(x['val'].split()[0]), reverse=True)[:5]
        }
        
        # Casos especiales
        if net == 'youtube':
            db_data['details'][net]["watch_time"] = sum(v.get('watchMinutes', 0) for v in data)

    with open('metricool_data.js', 'w', encoding='utf-8') as f:
        f.write(f"window.metricoolData = {json.dumps(db_data, indent=4, ensure_ascii=False)};")
    
    print(f"🚀 Proceso terminado. Redes con datos: {list(db_data['details'].keys())}")

if __name__ == "__main__":
    process_data()
