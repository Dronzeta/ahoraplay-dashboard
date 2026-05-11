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
        response = requests.get(url, headers=headers)
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
    
    # URL de posts (donde están las vistas)
    url = f"https://app.metricool.com/api/v1/analytics/posts/{network}"
    params = {
        "blogid": blog_id,
        "from": month_ago.strftime("%Y-%m-%d"),
        "to": today.strftime("%Y-%m-%d")
    }
    headers = {"X-Mc-Auth": AUTH_TOKEN}
    
    try:
        print(f"📡 Consultando {network}...")
        res = requests.get(url, params=params, headers=headers)
        if res.status_code == 200:
            data = res.json().get('data', [])
            if data:
                print(f"📊 {network}: RECIBIDOS {len(data)} POSTS. Primeras vistas: {data[0].get('views', 0)}")
                return data
            else:
                print(f"⚠️ {network}: La API respondió SUCCESS pero la lista de datos está VACÍA [].")
        else:
            print(f"❌ {network}: Error {res.status_code} - {res.text[:50]}")
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
        
        # Si no hay datos, ponemos un valor de prueba para saber si el JS está funcionando
        vistas = sum(int(v.get('views', 0) or v.get('viewCount', 0) or v.get('impressions', 0)) for v in data)
        posts = sorted([{"title": v.get('title') or v.get('text') or "Post", "val": f"{v.get('views', 0) or v.get('viewCount', 0)} v"} for v in data], key=lambda x: int(x['val'].split()[0]), reverse=True)[:6]
        
        db_data['details'][net] = {
            "total_views": vistas,
            "top_posts": posts
        }

    # FORZAR UN VALOR SI TODO DA 0 PARA DIAGNÓSTICO
    if sum(d['total_views'] for d in db_data['details'].values()) == 0:
        print("🚨 ATENCIÓN: Todos los datos dieron 0. Revisa los permisos de la API en Metricool.")

    with open('metricool_data.js', 'w', encoding='utf-8') as f:
        f.write(f"window.metricoolData = {json.dumps(db_data, indent=4, ensure_ascii=False)};")
    
    print("🚀 Proceso de guardado completado.")

if __name__ == "__main__":
    process_data()
