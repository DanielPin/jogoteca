from flask import Flask, flash, redirect, render_template, request, redirect, session


class Jogo:
    def __init__(self, nome, categoria, console):
        self.nome = nome
        self.categoria = categoria
        self.console = console


jogo1 = Jogo("Tetris", "Puzzle", "Atari")
jogo2 = Jogo("God of War", "Rack n Slash", "PS2")
jogo3 = Jogo("Mortal Kombate", "Luta", "PS3")
lista = [jogo1, jogo2, jogo3]

app = Flask(__name__)
app.secret_key = 'alura'

@app.route("/")
def index():
    return render_template("lista.html", titulo="Jogos", jogos=lista)


@app.route("/novo")
def nobo():
    return render_template("novo.html", titulo="Novo Jogo")


@app.route("/criar", methods=["POST"])
def criar():
    nome = request.form["nome"]
    categoria = request.form["categoria"]
    console = request.form["console"]

    jogo = Jogo(nome, categoria, console)
    lista.append(jogo)
    return redirect("/")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route('/autenticar', methods=['POST'])
def autenticar():
    if 'alohomora' == request.form['senha']:
        session['usuario_logado'] = request.form['usuario']
        flash(session['usuario_logado'] + ' logou com sucesso!')
        return redirect('/')
    else:
        flash('usuario nao logado!')
        return redirect('/login')

app.run(debug=True)
