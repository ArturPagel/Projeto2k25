from modelsTeste import UsuarioTeste
from config import *

app = Flask(__name__)
app.secret_key = "secret"  # Em produção, use uma chave secreta forte e segura

CAMINHO_FOTOS = os.path.join(os.getcwd(), "static", "imagens", "fotosperfil")

# --- ROTAS ---

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/auxiliar")
def auxiliar():
    return render_template("auxiliar.html")

@app.route("/acesso")
def acesso():
    return render_template("acesso.html")

@app.route("/acesso/cadastro")
def cadastro():
    return render_template("cadastro.html")

@app.route("/acesso/cadastro/novo_usuario", methods=["POST"])
def novo_usuario():
    nome = request.form.get("first_name")
    sobrenome = request.form.get("last_name")
    username = request.form.get("username")
    email = request.form.get("email")
    senha_raw = request.form.get("password")
    senha = generate_password_hash(senha_raw)
    foto = "/static/imagens/fotosperfil/default.jpg"  # foto padrão

    with db_session:
        existente_username = select(u for u in UsuarioTeste if u.username == username).limit(1).first()
        existente_email = select(u for u in UsuarioTeste if u.email == email).limit(1).first()
        
        if existente_username or existente_email:
            flash("Usuário ou email já cadastrado.", "error")
            return redirect(url_for("cadastro"))

        UsuarioTeste(
            nome=nome,
            sobrenome=sobrenome,
            username=username,
            email=email,
            senha=senha,
            foto=foto
        )
        commit()

    flash("Cadastro realizado com sucesso! Faça login.", "success")
    return redirect(url_for("login"))

@app.route("/acesso/login")
def login():
    return render_template("login.html")

@app.route("/acesso/login/usuario", methods=["POST"])
@db_session
def loginUser():
    login_usuario = request.form.get("login_user")
    senha = request.form.get("password")

    usuario = select(u for u in UsuarioTeste
                     if u.email == login_usuario or u.username == login_usuario).limit(1).first()

    if usuario and check_password_hash(usuario.senha, senha):
        session["nome"] = usuario.nome
        session["sobrenome"] = usuario.sobrenome
        session["username"] = usuario.username
        session["email"] = usuario.email
        session["foto_perfil"] = usuario.foto
        return redirect(url_for("home"))
    else:
        return render_template_string("""
            <script>
                alert("Email ou senha incorretos.");
                window.location.href = "/acesso/login";
            </script>
        """)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/perfil")
def perfil():
    return render_template("perfil.html")

@app.route("/perfil/atualizado", methods=["POST"])
def update_perfil():
    novo_nome = request.form.get("nome")
    novo_sobrenome = request.form.get("sobrenome")
    novo_username = request.form.get("username")
    novo_email = request.form.get("email")
    nova_foto = request.files.get("foto_perfil")

    with db_session:
        usuario = UsuarioTeste.get(email=session.get("email"))

        if not usuario:
            flash("Usuário não encontrado.", "error")
            return redirect(url_for("login"))

        usuario.nome = novo_nome
        usuario.sobrenome = novo_sobrenome
        usuario.username = novo_username
        usuario.email = novo_email

        if nova_foto and nova_foto.filename != '':
            nome_arquivo = secure_filename(nova_foto.filename)
            caminho_foto = os.path.join(CAMINHO_FOTOS, nome_arquivo)
            nova_foto.save(caminho_foto)
            url_foto = f'/static/imagens/fotosperfil/{nome_arquivo}'
            usuario.foto = url_foto
            session["foto_perfil"] = url_foto

        session["nome"] = novo_nome
        session["sobrenome"] = novo_sobrenome
        session["username"] = novo_username
        session["email"] = novo_email

        commit()
        flash("Perfil atualizado com sucesso!", "success")
        return redirect(url_for("perfil"))

@app.route("/sobre")
def sobre():
    return render_template("sobre.html")

# --- Roda o app ---
if __name__ == "__main__":
    app.run(debug=True)