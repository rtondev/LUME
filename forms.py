from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, TextAreaField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange, ValidationError
from models import User

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(message='Email é obrigatório'), Email(message='Email inválido')])
    senha = PasswordField('Senha', validators=[DataRequired(message='Senha é obrigatória'), Length(min=6, message='Senha deve ter no mínimo 6 caracteres')])
    remember_me = SelectField('Lembrar-me', choices=[('false', 'Não'), ('true', 'Sim')], default='false')
    submit = SubmitField('Entrar')

class CadastroForm(FlaskForm):
    nome = StringField('Nome Completo', validators=[DataRequired(message='Nome é obrigatório'), Length(min=3, max=100)])
    email = EmailField('Email', validators=[DataRequired(message='Email é obrigatório'), Email(message='Email inválido')])
    telefone = StringField('Telefone', validators=[Length(max=20)])
    senha = PasswordField('Senha', validators=[
        DataRequired(message='Senha é obrigatória'),
        Length(min=6, message='Senha deve ter no mínimo 6 caracteres')
    ])
    confirmar_senha = PasswordField('Confirmar Senha', validators=[
        DataRequired(message='Confirmação de senha é obrigatória'),
        EqualTo('senha', message='As senhas não coincidem')
    ])
    submit = SubmitField('Cadastrar')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Este email já está cadastrado. Use outro email ou faça login.')

class PersonalizacaoForm(FlaskForm):
    tamanho = SelectField('Tamanho', choices=[], validators=[DataRequired()])
    material = SelectField('Material', choices=[], validators=[DataRequired()])
    pedra = SelectField('Pedra', choices=[], validators=[DataRequired()])
    quantidade = IntegerField('Quantidade', validators=[DataRequired(), NumberRange(min=1, max=10)], default=1)
    submit = SubmitField('Adicionar ao Carrinho')

class AvaliacaoForm(FlaskForm):
    nota = SelectField('Nota', choices=[(5, '5'), (4, '4'), (3, '3'), (2, '2'), (1, '1')], validators=[DataRequired()], coerce=int)
    comentario = TextAreaField('Comentário', validators=[Length(max=500)])
    submit = SubmitField('Enviar Avaliação')

