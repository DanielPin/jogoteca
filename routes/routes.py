from flask import (
    flash,
    redirect,
    render_template,
    request,
    redirect,
    session,
    url_for,
    send_from_directory,
)
from jogoteca import app, db
from models.Jogos import Jogos
from models.Usuarios import Usuarios
from helper.helpers import (
    FormularioJogo,
    recupera_imagem,
    deleta_arquivo,
    FormularioUsuario,
)
import time
from flask_bcrypt import check_password_hash


@app.route("/")
def index():
    lista = Jogos.query.order_by(Jogos.id)
    return render_template("lista.html", titulo="Jogos", jogos=lista)


@app.route("/novo")
def novo():
    if "usuario_logado" not in session or session["usuario_logado"] == None:
        return redirect(url_for("login", proxima=url_for("novo")))
    form = FormularioJogo()
    return render_template("novo.html", titulo="Novo Jogo", form=form)


@app.route("/editar/<int:id>")
def editar(id):
    if "usuario_logado" not in session or session["usuario_logado"] == None:
        return redirect(url_for("login", proxima=url_for("editar", id=id)))
    jogo = Jogos.query.filter_by(id=id).first()
    form = FormularioJogo()

    form.nome.data = jogo.nome
    form.categoria.data = jogo.categoria
    form.console.data = jogo.console

    capa_jogo = recupera_imagem(id)
    if capa_jogo == None:
        capa_jogo = "capa_padrao.jpg"
    return render_template(
        "editar.html", titulo="Editando Jogo", id=id, capa_jogo=capa_jogo, form=form
    )


@app.route("/criar", methods=["POST"])
def criar():
    form = FormularioJogo(request.form)

    if not form.validate_on_submit():
        return redirect(url_for("novo"))

    nome = form.nome.data
    categoria = form.categoria.data
    console = form.console.data

    jogo = Jogos.query.filter_by(nome=nome).first()

    if jogo:
        flash("Este jogo já existe no banco de dados")
        return redirect(url_for("index"))

    novo_jogo = Jogos(nome=nome, categoria=categoria, console=console)
    db.session.add(novo_jogo)
    db.session.commit()

    arquivo = request.files["arquivo"]
    upload_path = app.config["UPLOAD_PATH"]
    timestamp = time.time()
    arquivo.save(f"{upload_path}/capa_{novo_jogo.id}-{timestamp}.jpg")

    return redirect(url_for("index"))


@app.route("/atualizar", methods=["POST"])
def atualizar():
    form = FormularioJogo(request.form)

    if form.validate_on_submit():
        jogo = Jogos.query.filter_by(id=request.form["id"]).first()
        jogo.nome = form.nome.data
        jogo.categoria = form.categoria.data
        jogo.console = form.console.data

        db.session.add(jogo)
        db.session.commit()

        arquivo = request.files["arquivo"]
        upload_path = app.config["UPLOAD_PATH"]
        timestamp = time.time()
        deleta_arquivo(jogo.id)
        arquivo.save(f"{upload_path}/capa_{jogo.id}-{timestamp}.jpg")

    return redirect(url_for("index"))


@app.route("/deletar/<int:id>")
def deletar(id):
    if "usuario_logado" not in session or session["usuario_logado"] == None:
        return redirect(url_for("login"))

    Jogos.query.filter_by(id=id).delete()
    db.session.commit()
    flash("Jogo deletado com sucesso")
    return redirect(url_for("index"))


@app.route("/login")
def login():
    proxima = request.args.get("proxima")
    form = FormularioUsuario()
    return render_template("login.html", proxima=proxima, form=form)


@app.route("/autenticar", methods=["POST"])
def autenticar():
    form = FormularioUsuario(request.form)
    usuario = Usuarios.query.filter_by(nickname=form.nickname.data).first()
    senha = check_password_hash(usuario.senha, form.senha.data)
    if usuario and senha:
        session["usuario_logado"] = usuario.nickname
        flash(usuario.nickname + " logou com sucesso!")
        proxima_pagina = request.form["proxima"]
        return redirect(proxima_pagina)

    else:
        flash("usuario nao logado!")
        return redirect(url_for("login"))


@app.route("/logout")
def logout():
    session["usuario_logado"] = None
    flash("usuario deslogado!")
    return redirect(url_for("index"))


@app.route("/uploads/<nome_arquivo>")
def imagem(nome_arquivo):
    return send_from_directory("uploads", nome_arquivo)
