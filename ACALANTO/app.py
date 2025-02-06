from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = 'socjksjdsjkjkkdsfds2356fds6g456sg45f6dg4f5d6'  # Necessário para usar mensagens flash
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///meu_banco.db'

db = SQLAlchemy(app)  # Certifique-se de que isso é definido antes das classes de modelo

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)  # Novo campo para nome
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(128), nullable=False)

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)
    
    def verificar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

class Gato(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    imunizado = db.Column(db.String(120), nullable=False)
    regiao = db.Column(db.String(120), nullable=False)
    genero = db.Column(db.String(120), nullable=False)
    observacao = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(120), nullable=False)
    imagem = db.Column(db.String(120), nullable=False)

# Cria todas as tabelas
with app.app_context():
    db.create_all()

    # Cria um administrador padrão se não existir
    if not Usuario.query.filter_by(email='admin@example.com').first():
        admin = Usuario(nome='ivan', email='admin@example.com')
        admin.set_senha('123')
        db.session.add(admin)
        db.session.commit()

@app.route('/')
def index():
    usuarios = Usuario.query.all()
    return render_template('index.html', usuarios=usuarios)

@app.route('/adicionar', methods=['POST'])
def adicionar():
    nome = request.form['nome']
    email = request.form['email']
    senha = request.form['senha']

    # Verifica se o email já está registrado
    if Usuario.query.filter_by(email=email).first():
        flash('Email já registrado!', 'danger')
        return redirect(url_for('index'))

    # Adiciona novo usuário
    novo_usuario = Usuario(nome=nome, email=email)
    novo_usuario.set_senha(senha)
    db.session.add(novo_usuario)
    db.session.commit()

    flash('Usuário registrado com sucesso!', 'success')
    return redirect(url_for('index'))

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        try:
            nome = request.form.get('nomeGato')
            imunizado = request.form.get('imunizadoGato')
            regiao = request.form.get('regiaoAdministrativaGato')
            genero = request.form.get('generoGato')
            observacao = request.form.get('observacaoGato')
            status = request.form.get('statusGato')
            imagem = request.files.get('imagemGato')

            # Verifica se todos os campos estão presentes
            if not all([nome, imunizado, regiao, genero, observacao, status, imagem]):
                flash('Todos os campos são obrigatórios!', 'danger')
                return redirect(url_for('cadastro'))

            # Salva a imagem no diretório 'static/img'
            img_path = os.path.join('static', 'img', imagem.filename)
            imagem.save(img_path)

            # Insere os dados no banco de dados
            novo_gato = Gato(nome=nome, imunizado=imunizado, regiao=regiao, genero=genero, 
                            observacao=observacao, status=status, imagem=img_path)
            db.session.add(novo_gato)
            db.session.commit()

            flash('Gato cadastrado com sucesso!', 'success')
            return redirect(url_for('cadastro'))
        except KeyError as e:
            return f"Erro: O campo '{e.args[0]}' não foi encontrado no formulário.", 400
        except Exception as e:
            return f"Ocorreu um erro: {e}", 500

    return render_template('cadastro.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nome = request.form.get('nome')
        senha = request.form.get('senha')

        if nome and senha:
            # Busca o usuário pelo nome
            usuario = Usuario.query.filter_by(nome=nome).first()

            # Verifica se o usuário existe e a senha está correta
            if usuario and usuario.verificar_senha(senha):
                session['user_id'] = usuario.id
                flash('Login realizado com sucesso!', 'success')
                return redirect(url_for('cadastro'))  # Redireciona para a página de cadastro de gatos
            else:
                flash('Nome ou senha inválidos!', 'danger')
        else:
            flash('Nome e senha são obrigatórios!', 'danger')

    return render_template('loginAdministrador.html')


@app.route('/paginaGestaoGatos')
def paginaGestaoGatos():
    return render_template('paginaGestaoGatos.html')

if __name__ == '__main__':
    app.run(debug=True)
