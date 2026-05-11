import json
import requests
import datetime
import os

# CONFIGURACIÓN
AUTH_TOKEN = "HIPVBFNGOGNLFVQQXVQEKDOKQNJMZLZCKRFDULSYVFMAFMIYUMJKOYZZNIHUCDEZ"

def get_valid_blog_id():
    print("🔍 Buscando Blog ID válido...")
    url = "https://app.metricool.com/api/v1/blogs"
    headers = {"X-Mc-Auth": AUTH_TOKEN}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            blogs = response.json()
            if blogs:
                # Agarramos el primero que tenga nombre o el primero de la lista
                blog_id = blogs[0].get('blogid') or blogs[0].get('id')
                print(f"✅ Blog encontrado: {blogs[0].get('name')} (ID: {blog_id})")
                return str(blog_id)
    except Exception as e:
        print(f"❌ Error buscando blogs: {e}")
    return "6130804" # Fallback al que ya teníamos

def fetch_metricool_data(blog_id, network):
    today = datetime.datetime.now()
    # CAMBIADO A 30 DÍAS como pediste
    month_ago = today - datetime.timedelta(days=30)
    
    # Probamos las dos rutas conocidas
    endpoints = [
        f"https://app.metricool.com/api/v1/analytics/posts/{network}",
        f"https://app.metricool.com/api/v1/analytics/{network}"
    ]
    
    params = {
        "blogid": blog_id,
        "from": month_ago.strftime("%Y-%m-%d"),
        "to": today.strftime("%Y-%m-%d")
    }
    
    headers = {"X-Mc-Auth": AUTH_TOKEN}
    
    for url in endpoints:
        try:
            print(f"📡 {network} -> {url[:50]}...")
            res = requests.get(url, params=params, headers=headers)
            if res.status_code == 200:
                data = res.json().get('data', [])
                if data:
                    print(f"✅ {network}: {len(data)} registros.")
                    return data
        except:
            continue
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
        if not data: continue
        
        # Sumar métricas
        vistas = sum(int(v.get('views', 0) or v.get('viewCount', 0) or v.get('impressions', 0)) for v in data)
        posts = sorted([{"title": v.get('title') or v.get('text') or "Post", "val": f"{v.get('views', 0) or v.get('viewCount', 0)} v"} for v in data], key=lambda x: int(x['val'].split()[0]), reverse=True)[:6]
        
        db_data['details'][net] = {
            "total_views": vistas,
            "top_posts": posts
        }

    with open('metricool_data.js', 'w', encoding='utf-8') as f:
        f.write(f"window.metricoolData = {json.dumps(db_data, indent=4, ensure_ascii=False)};")
    
    print(f"🚀 Dashboard actualizado (30 días).")

if __name__ == "__main__":
    process_data()
