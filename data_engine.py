import json
import requests
import datetime
import os

# CONFIGURACIÓN
AUTH_TOKEN = "HIPVBFNGOGNLFVQQXVQEKDOKQNJMZLZCKRFDULSYVFMAFMIYUMJKOYZZNIHUCDEZ"

# CABECERAS DE NAVEGADOR REAL para evitar el bloqueo de Metricool
HEADERS = {
    "X-Mc-Auth": AUTH_TOKEN,
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://app.metricool.com/",
    "Origin": "https://app.metricool.com"
}

def get_valid_blog_id():
    url = "https://app.metricool.com/api/v1/blogs"
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            blogs = response.json()
            if blogs:
                blog_id = str(blogs[0].get('blogid') or blogs[0].get('id'))
                print(f"✅ Blog Detectado: {blogs[0].get('name')} (ID: {blog_id})")
                return blog_id
    except: pass
    return "6130804"

def fetch_metricool_data(blog_id, network):
    today = datetime.datetime.now()
    month_ago = today - datetime.timedelta(days=30)
    
    # URL de posts
    url = f"https://app.metricool.com/api/v1/analytics/posts/{network}"
    params = {
        "blogid": blog_id,
        "from": month_ago.strftime("%Y-%m-%d"),
        "to": today.strftime("%Y-%m-%d")
    }
    
    try:
        print(f"📡 Consultando {network}...")
        res = requests.get(url, params=params, headers=HEADERS)
        
        if res.status_code == 200:
            data = res.json().get('data', [])
            print(f"📊 {network}: {len(data)} registros.")
            return data
        else:
            print(f"❌ {network}: Error {res.status_code}. El servidor bloqueó la petición.")
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
