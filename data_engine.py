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
    
    url = f"https://api.metricool.com/api/v1/analytics/{network}/{endpoint}?blogId={BLOG_ID}&from={date_from}&to={date_to}"
    
    print(f"🔍 Consultando: {network}...")
    
    req = urllib.request.Request(url)
    req.add_header("X-Mc-Auth", AUTH_TOKEN)
    
    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode()
            res_json = json.loads(res_body)
            
            # DIAGNÓSTICO: Ver qué trae la API
            if 'data' in res_json:
                count = len(res_json['data'])
                print(f"✅ {network}: Recibidos {count} registros.")
            else:
                print(f"⚠️ {network}: No hay campo 'data'. Respuesta: {res_body[:100]}")
                
            return res_json
    except urllib.error.HTTPError as e:
        print(f"❌ Error HTTP en {network}: {e.code} - {e.reason}")
        return None
    except Exception as e:
        print(f"❌ Error inesperado en {network}: {e}")
        return None

def process_data():
    networks = ['youtube', 'tiktok', 'instagram', 'twitter']
    raw_data = {net: fetch_metricool_data(net) for net in networks}
    
    db_data = {
        "last_update": datetime.datetime.now().strftime("%d %b, %H:%M"),
        "details": {}
    }
    
    for net, data in raw_data.items():
        if not data or 'data' not in data: continue
        items = data['data']
        if not items: continue
        
        if net == 'youtube':
            db_data['details']['youtube'] = {
                "total_views": sum(v.get('views', 0) for v in items),
                "watch_time": sum(v.get('watchMinutes', 0) for v in items),
                "videos": sorted([{"title": v.get('title', 'Video'), "val": f"{v.get('views',0)} v"} for v in items if v.get('videoType') == 'VIDEO'], key=lambda x: int(x['val'].split()[0]), reverse=True)[:6],
                "shorts": sorted(items, key=lambda x: x.get('views', 0), reverse=True)[:5]
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
                "interactions": sum(p.get('interactions', 0) for p in items)
            }
        elif net == 'twitter':
            db_data['details']['twitter'] = {
                "impressions": sum(p.get('impressions', 0) for p in items),
                "retweets": sum(p.get('retweets', 0) or p.get('shares', 0) for p in items),
                "top_posts": sorted(items, key=lambda x: x.get('interactions', 0), reverse=True)[:5]
            }

    output_js = 'metricool_data.js'
    with open(output_js, 'w', encoding='utf-8') as f:
        f.write(f"window.metricoolData = {json.dumps(db_data, indent=4, ensure_ascii=False)};")
    
    print(f"🚀 Dashboard generado con datos de {list(db_data['details'].keys())}")

if __name__ == "__main__":
    process_data()
