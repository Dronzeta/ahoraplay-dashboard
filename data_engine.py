import json
import urllib.request
import datetime
import os

# CONFIGURACIÓN
AUTH_TOKEN = "HIPVBFNGOGNLFVQQXVQEKDOKQNJMZLZCKRFDULSYVFMAFMIYUMJKOYZZNIHUCDEZ"
BLOG_ID = "6130804"

def fetch_metricool_data(network, endpoint="posts"):
    today = datetime.datetime.now()
    seven_days_ago = today - datetime.timedelta(days=7)
    date_from = seven_days_ago.strftime("%Y-%m-%dT00:00:00")
    date_to = today.strftime("%Y-%m-%dT23:59:59")
    
    # URL oficial de la API de Metricool
    url = f"https://app.metricool.com/api/v1/analytics/{network}/{endpoint}?blogId={BLOG_ID}&from={date_from}&to={date_to}"
    
    print(f"🔍 Consultando {network}...")
    req = urllib.request.Request(url)
    req.add_header("X-Mc-Auth", AUTH_TOKEN)
    
    try:
        with urllib.request.urlopen(req) as response:
            res_json = json.loads(response.read().decode())
            data_list = res_json.get('data', [])
            print(f"✅ {network}: {len(data_list)} registros encontrados.")
            return data_list
    except Exception as e:
        print(f"❌ Error en {network}: {e}")
        return []

def process_data():
    networks = ['youtube', 'tiktok', 'instagram', 'twitter']
    results = {net: fetch_metricool_data(net) for net in networks}
    
    db_data = {
        "last_update": datetime.datetime.now().strftime("%d %b, %H:%M"),
        "details": {}
    }
    
    # Procesar YouTube
    yt = results.get('youtube', [])
    if yt:
        db_data['details']['youtube'] = {
            "total_views": sum(v.get('views', 0) for v in yt),
            "watch_time": sum(v.get('watchMinutes', 0) for v in yt),
            "videos": sorted([{"title": v.get('title', 'Video'), "val": f"{v.get('views', 0)} v"} for v in yt if v.get('videoType') == 'VIDEO'], key=lambda x: int(x['val'].split()[0]), reverse=True)[:6],
            "shorts": sorted([{"title": v.get('title', 'Short'), "val": f"{v.get('views', 0)} v"} for v in yt if v.get('videoType') == 'SHORT'], key=lambda x: int(x['val'].split()[0]), reverse=True)[:5]
        }

    # Procesar TikTok
    tt = results.get('tiktok', [])
    if tt:
        db_data['details']['tiktok'] = {
            "total_views": sum(v.get('viewCount', 0) for v in tt),
            "avg_completion": (sum(v.get('fullVideoWatchedRate', 0) for v in tt) / len(tt)) if tt else 0,
            "top_posts": sorted([{"title": v.get('title') or "Video TikTok", "val": f"{v.get('viewCount', 0)} v"} for v in tt], key=lambda x: int(x['val'].split()[0]), reverse=True)[:5]
        }

    # Procesar Instagram
    ig = results.get('instagram', [])
    if ig:
        db_data['details']['instagram'] = {
            "reach": sum(v.get('reach', 0) for v in ig),
            "interactions": sum(v.get('interactions', 0) for v in ig)
        }

    # Guardar como JS
    with open('metricool_data.js', 'w', encoding='utf-8') as f:
        f.write(f"window.metricoolData = {json.dumps(db_data, indent=4, ensure_ascii=False)};")
    
    print("🚀 Dashboard actualizado correctamente.")

if __name__ == "__main__":
    process_data()
