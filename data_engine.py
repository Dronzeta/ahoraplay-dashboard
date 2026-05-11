import json
import requests
import datetime
import os

# CONFIGURACIÓN
AUTH_TOKEN = "HIPVBFNGOGNLFVQQXVQEKDOKQNJMZLZCKRFDULSYVFMAFMIYUMJKOYZZNIHUCDEZ"

def get_valid_blog_id():
    url = "https://app.metricool.com/api/v1/blogs"
    headers = {"X-Mc-Auth": AUTH_TOKEN}
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            blogs = res.json()
            if blogs: return str(blogs[0].get('blogid') or blogs[0].get('id'))
    except: pass
    return "6130804"

def fetch_metricool_data(blog_id, network):
    today = datetime.datetime.now()
    month_ago = today - datetime.timedelta(days=30)
    
    # URL MODERNA: Esta es la que usa la integración de n8n y la App móvil
    # El recurso es 'posts' y la red va como parámetro
    url = "https://app.metricool.com/api/v1/analytics/posts"
    
    params = {
        "blogid": blog_id,
        "network": network,
        "from": month_ago.strftime("%Y-%m-%d"),
        "to": today.strftime("%Y-%m-%d")
    }
    
    headers = {
        "X-Mc-Auth": AUTH_TOKEN,
        "Accept": "application/json"
    }
    
    try:
        print(f"📡 Consultando {network} (Ruta: analytics/posts)...")
        res = requests.get(url, params=params, headers=headers)
        
        if res.status_code == 200:
            data = res.json().get('data', [])
            print(f"✅ {network}: {len(data)} registros.")
            return data
        else:
            # ÚLTIMO INTENTO: Ruta antigua si la nueva falla
            url_alt = f"https://app.metricool.com/api/v1/analytics/{network}/posts"
            res_alt = requests.get(url_alt, params=params, headers=headers)
            if res_alt.status_code == 200:
                data = res_alt.json().get('data', [])
                print(f"✅ {network} (alt): {len(data)} registros.")
                return data
            
            print(f"❌ {network}: Falló con código {res.status_code}")
    except Exception as e:
        print(f"❌ Error en {network}: {e}")
    return []

def process_data():
    blog_id = get_valid_blog_id()
    networks = ['youtube', 'tiktok', 'instagram', 'twitter']
    
    db_data = {
        "last_update": datetime.datetime.now().strftime("%d %b, %H:%M"),
        "details": {}
    }
    
    for net in networks:
        data = fetch_metricool_data(blog_id, net)
        vistas = sum(int(v.get('views', 0) or v.get('viewCount', 0) or v.get('impressions', 0)) for v in data)
        posts = sorted([{"title": v.get('title') or v.get('text') or "Post", "val": f"{v.get('views', 0) or v.get('viewCount', 0)} v"} for v in data], key=lambda x: int(x['val'].split()[0]), reverse=True)[:6]
        
        db_data['details'][net] = {
            "total_views": vistas,
            "top_posts": posts
        }

    with open('metricool_data.js', 'w', encoding='utf-8') as f:
        f.write(f"window.metricoolData = {json.dumps(db_data, indent=4, ensure_ascii=False)};")
    
    print("🚀 Dashboard actualizado.")

if __name__ == "__main__":
    process_data()
