import json
import urllib.request
import datetime
import os

# CONFIGURACIÓN (Con UserId detectado en tu captura)
AUTH_TOKEN = "HIPVBFNGOGNLFVQQXVQEKDOKQNJMZLZCKRFDULSYVFMAFMIYUMJKOYZZNIHUCDEZ"
BLOG_ID = "6130804"
USER_ID = "4729482"

def fetch_metricool_data(network, endpoint="posts"):
    today = datetime.datetime.now()
    seven_days_ago = today - datetime.timedelta(days=7)
    date_from = seven_days_ago.strftime("%Y-%m-%dT00:00:00")
    date_to = today.strftime("%Y-%m-%dT23:59:59")
    
    # URL CON USERID (Vía recomendada por el panel de control)
    url = f"https://app.metricool.com/api/v1/analytics/{network}/{endpoint}?blogId={BLOG_ID}&userId={USER_ID}&from={date_from}&to={date_to}"
    
    print(f"🔍 Consultando {network}...")
    req = urllib.request.Request(url)
    req.add_header("X-Mc-Auth", AUTH_TOKEN)
    
    try:
        with urllib.request.urlopen(req) as response:
            res_json = json.loads(response.read().decode())
            data_list = res_json.get('data', [])
            print(f"✅ {network}: {len(data_list)} registros.")
            return data_list
    except Exception as e:
        # Intento sin /posts si falla el primero
        print(f"⚠️ Falló /posts en {network}. Probando ruta base...")
        url_alt = f"https://app.metricool.com/api/v1/analytics/{network}?blogId={BLOG_ID}&userId={USER_ID}&from={date_from}&to={date_to}"
        try:
            req_alt = urllib.request.Request(url_alt)
            req_alt.add_header("X-Mc-Auth", AUTH_TOKEN)
            with urllib.request.urlopen(req_alt) as res_alt:
                res_json = json.loads(res_alt.read().decode())
                data_list = res_json.get('data', [])
                print(f"✅ {network} (alt): {len(data_list)} registros.")
                return data_list
        except:
            print(f"❌ Error definitivo en {network}")
            return []

def process_data():
    networks = ['youtube', 'tiktok', 'instagram', 'twitter']
    results = {net: fetch_metricool_data(net) for net in networks}
    
    db_data = {
        "last_update": datetime.datetime.now().strftime("%d %b, %H:%M"),
        "details": {}
    }
    
    # Procesamiento simplificado para asegurar que no falle
    for net, data in results.items():
        if not data: continue
        
        if net == 'youtube':
            db_data['details']['youtube'] = {
                "total_views": sum(v.get('views', 0) for v in data),
                "watch_time": sum(v.get('watchMinutes', 0) for v in data),
                "videos": sorted([{"title": v.get('title', 'Video'), "val": f"{v.get('views', 0)} v"} for v in data], key=lambda x: int(x['val'].split()[0]) if x['val'].split()[0].isdigit() else 0, reverse=True)[:6]
            }
        elif net == 'tiktok':
            db_data['details']['tiktok'] = {
                "total_views": sum(v.get('viewCount', 0) for v in data),
                "top_posts": sorted([{"title": v.get('title', 'TikTok'), "val": f"{v.get('viewCount', 0)} v"} for v in data], key=lambda x: int(x['val'].split()[0]) if x['val'].split()[0].isdigit() else 0, reverse=True)[:5]
            }
        elif net == 'instagram':
            db_data['details']['instagram'] = {
                "reach": sum(v.get('reach', 0) for v in data),
                "interactions": sum(v.get('interactions', 0) for v in data)
            }

    with open('metricool_data.js', 'w', encoding='utf-8') as f:
        f.write(f"window.metricoolData = {json.dumps(db_data, indent=4, ensure_ascii=False)};")
    
    print("🚀 Dashboard actualizado con UserId.")

if __name__ == "__main__":
    process_data()
