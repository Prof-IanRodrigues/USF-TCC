from flask import Flask, render_template, request, send_file, session, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from fpdf import FPDF
from flask_session import Session

import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'USF_TCC'


app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

users = {}

# Lista para armazenar as referências geradas
referencias = []

# Classe para representar um usuário
class User(UserMixin):
        def __init__(self, id, password_hash):
            self.id = id
            self.password_hash = password_hash

@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)

@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users:
            flash("Usuário já existe!", "danger")
            return redirect(url_for('register'))

        # Criptografa a senha
        password_hash = generate_password_hash(password)

        # Cria o usuário e o adiciona ao "banco de dados"
        users[username] = User(username, password_hash)

        flash("Registro bem-sucedido! Agora faça login.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

# Rota de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = users.get(username)

        if user and check_password_hash(user.password_hash, password):
            login_user(user)  # Faz login do usuário
            session['username'] = username  # Armazena a sessão do usuário
            flash("Login bem-sucedido!", "success")
            return redirect(url_for('index'))
        else:
            flash("Credenciais inválidas, tente novamente.", "danger")
            return redirect(url_for('login'))

    return render_template('login.html')

# Rota protegida (apenas acessível a usuários logados)
@app.route('/index', methods=["GET", "POST"])
def index():
    username = session.get('username', 'Visitante')  # Recupera sessão do usuário
    
    if request.method == "POST":
        # Pega os dados do formulário
        tipo = request.form["tipo"]  # Tipo da referência
        sobrenomeautor = request.form["sobrenomeautor"]
        prenomeautor = request.form["prenomeautor"]
        titulo = request.form["titulo"]
        edicao = request.form.get("edicao", "")
        local = request.form["local"]
        editora = request.form.get("editora", "")
        ano = request.form["ano"]
        paginas = request.form.get("paginas", "")
        volume = request.form.get("volume", "")
        numero = request.form.get("numero", "")
        mes = request.form.get("mes", "")
        link = request.form.get("link", "")
        data_acesso = request.form.get("data_acesso", "")
        instituicao = request.form.get("instituicao", "")
        universidade = request.form.get("universidade", "")
        grau = request.form.get("grau", "")  # Mestrado, Doutorado ou Graduação
        nome_organizador = request.form.get("nome_organizador", "")
        citacao = request.form.get("citacao", "").strip()
        secao = request.form.get("secao", "").strip()

        if not tipo or not sobrenomeautor or not titulo or not ano or not local:
            return render_template("index.html", error="Por favor, preencha todos os campos obrigatórios.")
        
        # Divide o nome do autor para formatar corretamente
        sobrenomeautor = sobrenomeautor.upper()  # Último nome em maiúsculas
        partes_nome = prenomeautor.split()

        # Gera as iniciais
        iniciais = [parte[0] + '.' for parte in partes_nome]

        # Junta as iniciais formatadas em uma string
        iniciais_formatadas = " ".join(iniciais).upper()
        referencia_formatada =""
                # Formata a referência de acordo com o tipo
        if tipo == "Livro":
            referencia_formatada = f"{sobrenomeautor}, {iniciais_formatadas}. <strong>{titulo}</strong>. {edicao}. ed. {local}: {editora}, {ano}. p. {paginas}."
            if citacao:
                referencia_formatada += f"\nTrecho citado: \"{citacao}\""
            if secao:
                referencia_formatada += f"\nSeção onde será usada: {secao}"

        elif tipo == "Livro em parte":
            referencia_formatada = f"{sobrenomeautor}, {iniciais_formatadas}. {titulo}. In: {nome_organizador}. et al. (org.). <strong>{titulo}</strong>. {local}: {editora}, {ano}. p. {paginas}."
            if citacao:
                referencia_formatada += f"\nTrecho citado: \"{citacao}\""
            if secao:
                referencia_formatada += f"\nSeção onde será usada: {secao}"

        elif tipo == "Tese":
            referencia_formatada = f"{sobrenomeautor}, {iniciais_formatadas}. <strong>{titulo}</strong>. {ano}. p. {paginas}. Tese ({grau} em {instituicao}) - {universidade}, {local}, {ano}."
            if citacao:
                referencia_formatada += f"\nTrecho citado: \"{citacao}\""
            if secao:
                referencia_formatada += f"\nSeção onde será usada: {secao}"

        elif tipo == "Dissertação":
            referencia_formatada = f"{sobrenomeautor}, {iniciais_formatadas}. <strong>{titulo}</strong>. {ano}. p. {paginas}. Dissertação ({grau} em {instituicao}) - {universidade}, {local}, {ano}."
            if citacao:
                referencia_formatada += f"\nTrecho citado: \"{citacao}\""
            if secao:
                referencia_formatada += f"\nSeção onde será usada: {secao}"

        elif tipo == "TCC":
            referencia_formatada = f"{sobrenomeautor}, {iniciais_formatadas}. <strong>{titulo}</strong>. {ano}. p. {paginas}. Trabalho de Conclusão de Curso ({grau} em {instituicao}) - {universidade}, {local}, {ano}."
            if citacao:
                referencia_formatada += f"\nTrecho citado: \"{citacao}\""
            if secao:
                referencia_formatada += f"\nSeção onde será usada: {secao}"

        elif tipo == "Artigo de Periódico":
            referencia_formatada = f"{sobrenomeautor}, {iniciais_formatadas}. <strong>{titulo}</strong>. {edicao}. ed., {local}: {editora}, v. {volume}, n. {numero}, p. {paginas}, {mes}. {ano}. Disponível em: {link}. Acesso em: {data_acesso}."
            if citacao:
                referencia_formatada += f"\nTrecho citado: \"{citacao}\""
            if secao:
                referencia_formatada += f"\nSeção onde será usada: {secao}"

        elif tipo == "Referência Legislativa (CF)":
            referencia_formatada = f"BRASIL. [Constituição (1988)]. <strong>Constituição da República Federativa do Brasil</strong>. Brasília, DF: Senado Federal, {ano}. p. {paginas}. Disponível em: {link}. Acesso em: {data_acesso}."
            if citacao:
                referencia_formatada += f"\nTrecho citado: \"{citacao}\""
            if secao:
                referencia_formatada += f"\nSeção onde será usada: {secao}"

        elif tipo == "Referência Legislativa (Lei)":
            referencia_formatada = f"BRASIL. Lei nº {titulo}, de {ano}. {editora}. Diário Oficial da União: seção 1, Brasília, DF, ano {ano}, n. {numero}, p. {paginas}, {mes} {ano}."
            if citacao:
                referencia_formatada += f"\nTrecho citado: \"{citacao}\""
            if secao:
                referencia_formatada += f"\nSeção onde será usada: {secao}"

        elif tipo == "Referência Legislativa (Portaria/Resolução)":
            referencia_formatada = f"{local} (Estado). Resolução nº {titulo}, de {ano}. {editora}. Diário Oficial [{local}], {local}, v. {volume}, n. {numero}, p. {paginas}, {mes} {ano}. Disponível em: {link}. Acesso em: {data_acesso}."
            if citacao:
                referencia_formatada += f"\nTrecho citado: \"{citacao}\""
            if secao:
                referencia_formatada += f"\nSeção onde será usada: {secao}"

        elif tipo == "Texto na Internet":
            referencia_formatada = f"{sobrenomeautor}, {iniciais_formatadas}. <strong>{titulo}</strong>. {local}: {editora}, {ano}. p. {paginas}. Disponível em: {link}. Acesso em: {data_acesso}."
            if citacao:
                referencia_formatada += f"\nTrecho citado: \"{citacao}\""
            if secao:
                referencia_formatada += f"\nSeção onde será usada: {secao}"

    # Adiciona a referência à lista
        referencias.append(referencia_formatada)

    return render_template("index.html", referencias=referencias)

# Rota de logout
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("Você foi desconectado.", "info")
    return redirect(url_for('login'))

@app.route("/download", methods=["POST"])
def download():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for ref in referencias:
        ref = ref.replace("<strong>", "**").replace("</strong>", "**")  # Marca temporária

        parts = ref.split("**")
        bold = False

        for part in parts:
            if bold:
                pdf.set_font("Arial", "B", 12)  # Negrito
            else:
                pdf.set_font("Arial", "", 12)  # Normal

            pdf.write(6, part)  # Usa write() para manter a linha

            bold = not bold  # Alterna entre normal/negrito

        pdf.ln(6)  # Espaço entre referências

    pdf_file = "referencias.pdf"
    pdf.output(pdf_file)

    response = send_file(pdf_file, as_attachment=True)
    
    os.remove(pdf_file)

    return response

# Inicia o servidor
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
