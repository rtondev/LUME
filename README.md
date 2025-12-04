# Lume - Sistema de E-commerce para Aliança Solitária

Sistema desenvolvido em Flask para comercialização de anéis solitários, seguindo as especificações do projeto PDSI.

## Características

- Sistema de autenticação seguro com Flask-Login e Flask-WTF
- Interface moderna usando Preline UI e Tailwind CSS
- Personalização de produtos (tamanho, material, pedra)
- Simulação de preço em tempo real
- Carrinho de compras e checkout
- Sistema de avaliações
- Favoritos
- Histórico de pedidos

## Paleta de Cores

- **Dourado**: #C9A24B
- **Grafite**: #383732
- **Branco**: #FFFFFF

## Tipografia

- **Logo**: Cinzel
- **Títulos**: Lora
- **Textos e Menus**: Poppins

## Instalação

1. Crie um ambiente virtual (recomendado):
```bash
python -m venv venv
```

2. Ative o ambiente virtual:
   - **Windows (PowerShell):**
   ```bash
   .\venv\Scripts\Activate.ps1
   ```
   - **Windows (CMD):**
   ```bash
   venv\Scripts\activate.bat
   ```
   - **Linux/Mac:**
   ```bash
   source venv/bin/activate
   ```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Execute o aplicativo:
```bash
python app.py
```

5. Acesse no navegador:
```
http://localhost:5000
```

**Nota:** Sempre ative o ambiente virtual antes de trabalhar no projeto. Para desativar, digite `deactivate`.

## Estrutura do Projeto

```
lume/
├── app.py              # Aplicação principal Flask
├── config.py          # Configurações
├── models.py           # Modelos de banco de dados
├── forms.py            # Formulários WTForms
├── requirements.txt    # Dependências
├── templates/          # Templates HTML
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── cadastro.html
│   ├── produto.html
│   ├── carrinho.html
│   ├── checkout.html
│   └── pedidos.html
└── static/
    ├── css/
    │   └── custom.css
    └── imgs/
        └── logo.png
```

## Funcionalidades Implementadas

### Requisitos Funcionais (RF)

- ✅ RF01: Catálogo de produtos
- ✅ RF02: Personalização do anel (tamanho, material, pedra)
- ✅ RF03: Simulação de preço em tempo real
- ✅ RF04: Carrinho de compras e checkout
- ✅ RF05: Meios de pagamento (Pix, cartão, boleto)
- ✅ RF06: Cadastro/Login seguro
- ✅ RF07: Sistema de avaliações
- ✅ RF08: Rastreamento de pedidos

### Segurança

- Hash de senhas com Werkzeug (bcrypt)
- Proteção CSRF com Flask-WTF
- Limitação de tentativas de login (Flask-Limiter)
- Cookies seguros configurados
- Validação de formulários

## Tecnologias Utilizadas

- Flask 3.0.0
- Flask-SQLAlchemy
- Flask-Login
- Flask-WTF
- Flask-Limiter
- Preline UI
- Tailwind CSS

## Desenvolvido por

- Ingrid Leticia do Nascimento
- Ryan Kauê Batista da Silva
- Sheylla Mayara Soares da Silva

