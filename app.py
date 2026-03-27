import os
from flask import Flask, render_template, request, redirect, url_for
from supabase import create_client, Client

app = Flask(__name__)

# Configurações do Supabase (Pegue no painel do Supabase)
SUPABASE_URL = "SUA_URL_AQUI"
SUPABASE_KEY = "SUA_CHAVE_AQUI"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_user_ip():
    # No Render, o IP real vem neste cabeçalho
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0]
    return request.remote_addr

@app.route('/')
def index():
    user_ip = get_user_ip()
    # Busca todas as categorias
    response = supabase.table('categorias').select("*").execute()
    categorias = response.data
    return render_template('index.html', categorias=categorias, user_ip=user_ip)

@app.route('/criar_categoria', methods=['POST'])
def criar_categoria():
    nome = request.form.get('nome')
    ip = get_user_ip()
    supabase.table('categorias').insert({"nome": nome, "criador_ip": ip}).execute()
    return redirect(url_for('index'))

@app.route('/categoria/<id>')
def ver_categoria(id):
    user_ip = get_user_ip()
    # Busca a categoria e os livros dela
    cat = supabase.table('categorias').select("*").eq("id", id).single().execute()
    livros = supabase.table('livros').select("*").eq("categoria_id", id).execute()
    
    return render_template('categoria.html', categoria=cat.data, livros=livros.data, user_ip=user_ip)

@app.route('/postar_livro/<cat_id>', methods=['POST'])
def postar_livro(cat_id):
    user_ip = get_user_ip()
    # Verifica se o IP de quem está postando é o mesmo de quem criou a categoria
    cat = supabase.table('categorias').select("criador_ip").eq("id", cat_id).single().execute()
    
    if cat.data['criador_ip'] == user_ip:
        img_url = request.form.get('img_url') # Aqui você usaria o Storage do Supabase
        desc = request.form.get('descricao')
        supabase.table('livros').insert({
            "categoria_id": cat_id, 
            "imagem_url": img_url, 
            "descricao": desc,
            "criador_ip": user_ip
        }).execute()
    
    return redirect(url_for('ver_categoria', id=cat_id))

if __name__ == '__main__':
    app.run(debug=True)
