from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import check_password_hash
from functools import wraps
from models import db, User, Produto, Material, Pedra, Tamanho, Pedido, ItemPedido, Avaliacao, Favorito
from forms import LoginForm, CadastroForm, PersonalizacaoForm, AvaliacaoForm
from config import Config
from datetime import datetime
from decimal import Decimal

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'
login_manager.login_message_category = 'info'

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Acesso negado. Você precisa ser administrador.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def init_db():
    with app.app_context():
        db.create_all()
        
        if not Produto.query.first():
            produto = Produto(
                nome="Anel Solitário Lume",
                descricao="Um anel que captura a essência da luz e da elegância. Cada detalhe foi cuidadosamente pensado para transmitir sofisticação e significado único. O brilho do diamante central reflete não apenas a luz, mas também os sentimentos mais profundos.",
                preco_base=Decimal('2999.00'),
                imagem_url="/static/imgs/logo.png",
                ativo=True
            )
            db.session.add(produto)
            
            materiais = [
                Material(nome="Ouro 18k", preco_adicional=Decimal('500.00')),
                Material(nome="Ouro 14k", preco_adicional=Decimal('300.00')),
                Material(nome="Prata 925", preco_adicional=Decimal('0.00'))
            ]
            for material in materiais:
                db.session.add(material)
            
            pedras = [
                Pedra(nome="Diamante", preco_adicional=Decimal('1000.00')),
                Pedra(nome="Rubi", preco_adicional=Decimal('600.00')),
                Pedra(nome="Safira", preco_adicional=Decimal('600.00')),
                Pedra(nome="Esmeralda", preco_adicional=Decimal('500.00'))
            ]
            for pedra in pedras:
                db.session.add(pedra)
            
            tamanhos = [Tamanho(tamanho=str(i)) for i in range(10, 21)]
            for tamanho in tamanhos:
                db.session.add(tamanho)
            
            if not User.query.filter_by(email="admin@lume.com").first():
                admin = User(
                    nome="Administrador",
                    email="admin@lume.com",
                    is_admin=True
                )
                admin.set_password("admin123")
                db.session.add(admin)
            
            db.session.commit()

init_db()

@app.route('/')
def index():
    produtos = Produto.query.filter_by(ativo=True).all()
    return render_template('index.html', produtos=produtos)

@app.route('/produto/<int:id>')
def produto(id):
    produto = Produto.query.get_or_404(id)
    materiais = Material.query.all()
    pedras = Pedra.query.all()
    tamanhos = Tamanho.query.all()
    avaliacoes = Avaliacao.query.filter_by(produto_id=id).order_by(Avaliacao.created_at.desc()).limit(10).all()
    
    form = PersonalizacaoForm()
    form.tamanho.choices = [(t.tamanho, t.tamanho) for t in tamanhos]
    form.material.choices = [(m.id, f"{m.nome} (+R$ {m.preco_adicional:.2f})") for m in materiais]
    form.pedra.choices = [(p.id, f"{p.nome} (+R$ {p.preco_adicional:.2f})") for p in pedras]
    
    favoritado = False
    if current_user.is_authenticated:
        favorito = Favorito.query.filter_by(usuario_id=current_user.id, produto_id=id).first()
        favoritado = favorito is not None
    
    return render_template('produto.html', produto=produto, form=form, 
                         materiais=materiais, pedras=pedras, tamanhos=tamanhos,
                         avaliacoes=avaliacoes, favoritado=favoritado)

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.check_password(form.senha.data):
            remember = form.remember_me.data == 'true'
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            flash('Login realizado com sucesso!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Email ou senha incorretos.', 'error')
    
    return render_template('login.html', form=form)

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = CadastroForm()
    if form.validate_on_submit():
        user = User(
            nome=form.nome.data,
            email=form.email.data,
            telefone=form.telefone.data,
            is_admin=False
        )
        user.set_password(form.senha.data)
        db.session.add(user)
        db.session.commit()
        flash('Cadastro realizado com sucesso! Faça login para continuar.', 'success')
        return redirect(url_for('login'))
    
    return render_template('cadastro.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('index'))

@app.route('/calcular_preco', methods=['POST'])
def calcular_preco():
    data = request.get_json()
    produto_id = data.get('produto_id')
    material_id = data.get('material_id')
    pedra_id = data.get('pedra_id')
    
    produto = Produto.query.get(produto_id)
    material = Material.query.get(material_id)
    pedra = Pedra.query.get(pedra_id)
    
    if not all([produto, material, pedra]):
        return jsonify({'error': 'Dados inválidos'}), 400
    
    preco_total = float(produto.preco_base) + float(material.preco_adicional) + float(pedra.preco_adicional)
    
    return jsonify({'preco': preco_total, 'preco_formatado': f'R$ {preco_total:,.2f}'.replace(',', '.')})

@app.route('/favoritar/<int:produto_id>', methods=['POST'])
@login_required
def favoritar(produto_id):
    favorito = Favorito.query.filter_by(usuario_id=current_user.id, produto_id=produto_id).first()
    
    if favorito:
        db.session.delete(favorito)
        db.session.commit()
        return jsonify({'favoritado': False, 'message': 'Removido dos favoritos'})
    else:
        favorito = Favorito(usuario_id=current_user.id, produto_id=produto_id)
        db.session.add(favorito)
        db.session.commit()
        return jsonify({'favoritado': True, 'message': 'Adicionado aos favoritos'})

@app.route('/adicionar_carrinho', methods=['POST'])
@login_required
def adicionar_carrinho():
    data = request.get_json()
    produto_id = data.get('produto_id')
    quantidade = data.get('quantidade', 1)
    tamanho = data.get('tamanho')
    material_id = data.get('material_id')
    pedra_id = data.get('pedra_id')
    
    produto = Produto.query.get(produto_id)
    material = Material.query.get(material_id)
    pedra = Pedra.query.get(pedra_id)
    
    if not all([produto, material, pedra]):
        return jsonify({'error': 'Dados inválidos'}), 400
    
    preco_unitario = float(produto.preco_base) + float(material.preco_adicional) + float(pedra.preco_adicional)
    
    if 'carrinho' not in session:
        session['carrinho'] = []
    
    item = {
        'produto_id': produto_id,
        'quantidade': quantidade,
        'tamanho': tamanho,
        'material': material.nome,
        'pedra': pedra.nome,
        'preco_unitario': preco_unitario,
        'subtotal': preco_unitario * quantidade
    }
    
    session['carrinho'].append(item)
    session.modified = True
    
    return jsonify({'success': True, 'message': 'Produto adicionado ao carrinho', 'carrinho_count': len(session['carrinho'])})

@app.route('/carrinho')
@login_required
def carrinho():
    carrinho = session.get('carrinho', [])
    total = sum(item['subtotal'] for item in carrinho)
    return render_template('carrinho.html', carrinho=carrinho, total=total)

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    carrinho = session.get('carrinho', [])
    if not carrinho:
        flash('Seu carrinho está vazio.', 'warning')
        return redirect(url_for('carrinho'))
    
    total = sum(item['subtotal'] for item in carrinho)
    
    if request.method == 'POST':
        metodo_pagamento = request.form.get('metodo_pagamento')
        
        pedido = Pedido(
            usuario_id=current_user.id,
            status='pendente',
            total=Decimal(str(total)),
            metodo_pagamento=metodo_pagamento
        )
        db.session.add(pedido)
        db.session.flush()
        
        for item in carrinho:
            item_pedido = ItemPedido(
                pedido_id=pedido.id,
                produto_id=item['produto_id'],
                quantidade=item['quantidade'],
                tamanho=item['tamanho'],
                material=item['material'],
                pedra=item['pedra'],
                preco_unitario=Decimal(str(item['preco_unitario'])),
                subtotal=Decimal(str(item['subtotal']))
            )
            db.session.add(item_pedido)
        
        db.session.commit()
        session['carrinho'] = []
        session.modified = True
        
        flash('Pedido realizado com sucesso!', 'success')
        return redirect(url_for('pedidos'))
    
    return render_template('checkout.html', carrinho=carrinho, total=total)

@app.route('/pedidos')
@login_required
def pedidos():
    pedidos = Pedido.query.filter_by(usuario_id=current_user.id).order_by(Pedido.created_at.desc()).all()
    return render_template('pedidos.html', pedidos=pedidos)

@app.route('/avaliar/<int:produto_id>', methods=['POST'])
@login_required
def avaliar(produto_id):
    form = AvaliacaoForm()
    if form.validate_on_submit():
        avaliacao = Avaliacao(
            produto_id=produto_id,
            usuario_id=current_user.id,
            nota=form.nota.data,
            comentario=form.comentario.data
        )
        db.session.add(avaliacao)
        db.session.commit()
        flash('Avaliação enviada com sucesso!', 'success')
    
    return redirect(url_for('produto', id=produto_id))

@app.route('/admin/pedidos')
@admin_required
def admin_pedidos():
    pedidos = Pedido.query.order_by(Pedido.created_at.desc()).all()
    return render_template('admin/pedidos.html', pedidos=pedidos)

@app.route('/admin/pedido/<int:pedido_id>')
@admin_required
def admin_pedido_detalhes(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)
    return render_template('admin/pedido_detalhes.html', pedido=pedido)

@app.route('/admin/pedido/<int:pedido_id>/atualizar-status', methods=['POST'])
@admin_required
def admin_atualizar_status(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)
    novo_status = request.form.get('status')
    
    if novo_status in ['pendente', 'processando', 'enviado', 'entregue', 'cancelado']:
        pedido.status = novo_status
        db.session.commit()
        flash(f'Status do pedido #{pedido_id} atualizado para {novo_status}.', 'success')
    else:
        flash('Status inválido.', 'error')
    
    return redirect(url_for('admin_pedido_detalhes', pedido_id=pedido_id))

@app.route('/admin/produtos')
@admin_required
def admin_produtos():
    produtos = Produto.query.all()
    return render_template('admin/produtos.html', produtos=produtos)

@app.route('/admin/produto/novo', methods=['GET', 'POST'])
@admin_required
def admin_produto_novo():
    if request.method == 'POST':
        produto = Produto(
            nome=request.form.get('nome'),
            descricao=request.form.get('descricao'),
            preco_base=Decimal(request.form.get('preco_base')),
            imagem_url=request.form.get('imagem_url'),
            ativo=request.form.get('ativo') == 'on'
        )
        db.session.add(produto)
        db.session.commit()
        flash('Produto cadastrado com sucesso!', 'success')
        return redirect(url_for('admin_produtos'))
    
    return render_template('admin/produto_form.html')

@app.route('/admin/produto/<int:produto_id>/editar', methods=['GET', 'POST'])
@admin_required
def admin_produto_editar(produto_id):
    produto = Produto.query.get_or_404(produto_id)
    
    if request.method == 'POST':
        produto.nome = request.form.get('nome')
        produto.descricao = request.form.get('descricao')
        produto.preco_base = Decimal(request.form.get('preco_base'))
        produto.imagem_url = request.form.get('imagem_url')
        produto.ativo = request.form.get('ativo') == 'on'
        db.session.commit()
        flash('Produto atualizado com sucesso!', 'success')
        return redirect(url_for('admin_produtos'))
    
    return render_template('admin/produto_form.html', produto=produto)

@app.route('/admin/produto/<int:produto_id>/remover', methods=['POST'])
@admin_required
def admin_produto_remover(produto_id):
    produto = Produto.query.get_or_404(produto_id)
    db.session.delete(produto)
    db.session.commit()
    flash('Produto removido com sucesso!', 'success')
    return redirect(url_for('admin_produtos'))

if __name__ == '__main__':
    app.run(debug=True)

