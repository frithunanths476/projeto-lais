from flask import Flask, render_template, request, flash, redirect, url_for, send_from_directory, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/livros'
db = SQLAlchemy(app)

class Livro(db.Model):
    id_livro = db.Column(db.Integer, primary_key=True,autoincrement=True)
    titulo = db.Column(db.String(100))
    autor = db.Column(db.String(254))
    ano_publicacao = db.Column(db.Integer)

class Usuario(db.Model):
    id_usuario = db.Column(db.Integer, primary_key=True, auto_increment=True)
    email = db.Column(db.String(254))
    senha = db.Column(db.String(100))

@app.route('/main')
def index():
    livros = Livro.query.all()
    return render_template('cadastro_livros.html', outro=livros)

@app.route('/novo')
def novo():
    if 'user_id' in session:
        return render_template('novo.html', titulo='Novo Livro')
    else:
        return redirect(url_for('index'))

@app.route('/criar', methods=['POST'])
def criar():
    titulo = request.form['titulo']
    autor = request.form['autor']
    ano_publicacao = request.form['ano_publicacao']

    livro = Livro.query.filter_by(titulo=titulo).first()
    if livro:
       flash("Livro já existente!")
       return redirect(url_for('novo'))

    novo_livro = Livro(titulo=titulo, autor=autor, ano_publicacao=ano_publicacao)

    db.session.add(novo_livro)
    db.session.commit()

    arquivo = request.files['arquivo']
    arquivo.save(f'uploads/capa{novo_livro.id_livro}.jpg')

@app.route('/editar/<int:id>')
def editar(id):
    if 'user_id' in session:
        livro = Livro.query.filter_by(id_livro=id).first()
        return render_template('editar.html', titulo='Editando Livro', livro=livro)
    else:
        return redirect(url_for('index'))

@app.route('/deletar/<int:id>')
def deletar(id):
    Livro.query.filter_by(id_livro=id).delete()
    db.session.commit()
    flash('Livro excluido com sucesso.')
    return redirect(url_for('index'))

@app.route('/atualizar', methods=['POST'])
def atualizar():
   livro = Livro.query.filter_by(id_livro=request.form['id']).first()
   livro.titulo = request.form['titulo']
   livro.autor = request.form['autor']
   livro.ano_publicacao = request.form['ano_publicacao']


   db.session.add(livro)
   db.session.commit()

   return redirect(url_for('index'))

@app.route('/uploads/<nome_arquivo>')
def imagem(nome_arquivo):
    return send_from_directory('uploads', nome_arquivo)

@app.route('/')
def login_form():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    senha = request.form.get('senha')

    user = Usuario.query.filter_by(email=email).first()
    senha = check_password_hash(user.senha, senha)
    if user and senha:
        session['user_id'] = user.id_usuario
        if 'next' in session:
            next_route = session.pop('next')
            return redirect(url_for(next_route))
        return redirect(url_for('index'))
    else:
        flash('Email ou senha incorretos', 'error')
        return redirect(url_for('login_form'))

@app.route('/logout', methods=['POST'])
def logout():
    # Remova as chaves da sessão relacionadas ao usuário autenticado
    session.pop('user_id', None)
    # Redirecione para a página inicial ou outra página após o logout
    return redirect(url_for('login_form'))


@app.route('/novo_user')
def novo_user():
	return render_template('novo_usuario.html', titulo='Novo Usuário')

@app.route('/criar_user', methods=['POST'])
def criar_user():
    email = request.form['email']
    senha = request.form['senha']

    user = Usuario.query.filter_by(email=email).first()
    if user:
        flash('Usuário já existe', 'error')
        return redirect(url_for('novo_user'))
    else:
        senha_hash = generate_password_hash(senha).decode('utf-8')
        novo_usuario = Usuario(email=email, senha=senha_hash)
        db.session.add(novo_usuario)
        db.session.commit()
        flash('Usuário cadastrado com sucesso', 'success')
        return redirect(url_for('novo_user'))

if __name__ == '__main__':
    app.run()