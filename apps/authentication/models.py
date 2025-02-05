# -*- encoding: utf-8 -*-
from flask_login import UserMixin
from apps import db, login_manager
from datetime import date
from apps.authentication.util import hash_pass

# Table des Maladies
class Maladie(db.Model):
    __tablename__ = 'maladie'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    nom_commun = db.Column(db.String(255), nullable=False)
    nom_fon = db.Column(db.String(255), nullable=False)
    proprietes = db.Column(db.Text)
    images = db.Column(db.String(255))  # Chemin ou URL de l'image
    date_ajout = db.Column(db.Date, default=date.today) 
    date_mise_a_jour = db.Column(db.Date, onupdate=db.func.current_date())
    # Relation avec les remèdes
    remedes = db.relationship('RemedeMaladie', back_populates='maladie', cascade='all, delete-orphan')
    # Contrainte d'unicité
    __table_args__ = (
        db.UniqueConstraint('nom_commun', name='unique_nom_commun_maladie'),
    )

# Table des Ingrédients
class Ingredient(db.Model):
    __tablename__ = 'ingredients'
    id = db.Column(db.Integer, primary_key=True)
    like = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    nom_commun = db.Column(db.String(255), nullable=False)
    nom_fon = db.Column(db.String(255), nullable=False)
    nom_scientifique = db.Column(db.String(255))
    partie = db.Column(db.String(255))
    proprietes = db.Column(db.Text)
    latitude = db.Column(db.Float)  # Coordonnées géographiques
    longitude = db.Column(db.Float)
    images = db.Column(db.String(255))  # Chemin ou URL de l'image
    date_ajout = db.Column(db.Date, default=date.today) 
    date_mise_a_jour = db.Column(db.Date, onupdate=db.func.current_date())
    # Relation avec les remèdes
    remedes = db.relationship('RemedeIngredient', back_populates='ingredient', cascade='all, delete-orphan')
    articles = db.relationship('Article', secondary='article_ingredient', back_populates='ingredients')
    # Contrainte d'unicité
    __table_args__ = (
        db.UniqueConstraint('nom_scientifique', 'partie', name='unique_nom_scientifique_partie'),
    )

# Table des Remèdes
class Remede(db.Model):
    __tablename__ = 'remedes'
    id = db.Column(db.Integer, primary_key=True)
    like = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    nom = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    preparation = db.Column(db.Text)
    latitude = db.Column(db.Float)  # Coordonnées géographiques
    longitude = db.Column(db.Float)
    indications = db.Column(db.Text)
    dosage = db.Column(db.Text)
    precautions = db.Column(db.Text)
    video = db.Column(db.String(255))  # Chemin ou URL de la vidéo
    images = db.Column(db.String(255))  # Chemin ou URL de l'image
    liens = db.Column(db.String(255))  # Lien utile (ex: article ou source)
    date_ajout = db.Column(db.Date, default=db.func.current_date())
    date_mise_a_jour = db.Column(db.Date, onupdate=db.func.current_date())
    # Relation avec les ingrédients
    ingredients = db.relationship('RemedeIngredient', back_populates='remede', cascade='all, delete-orphan')
    # Relation avec les maladies
    maladie = db.relationship('RemedeMaladie', back_populates='remede', cascade='all, delete-orphan')
    articles = db.relationship('Article', secondary='article_remede', back_populates='remedes')
    __table_args__ = (
        db.UniqueConstraint('nom', name='unique_nom_remede'),
    )
    
# Table de liaison entre Remèdes et Ingrédients
class RemedeIngredient(db.Model):
    __tablename__ = 'remedes_ingredients'
    remede_id = db.Column(db.Integer, db.ForeignKey('remedes.id'), primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.id'), primary_key=True)
    quantite = db.Column(db.String(255))
    # Relations pour navigation
    remede = db.relationship('Remede', back_populates='ingredients')
    ingredient = db.relationship('Ingredient', back_populates='remedes')



class RemedeMaladie(db.Model):
    __tablename__ = 'remedes_maladie'
    remede_id = db.Column(db.Integer, db.ForeignKey('remedes.id'), primary_key=True)
    maladie_id = db.Column(db.Integer, db.ForeignKey('maladie.id'), primary_key=True)
    # Relations pour navigation
    remede = db.relationship('Remede', back_populates='maladie')
    maladie = db.relationship('Maladie', back_populates='remedes')

class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(255), nullable=False)
    auteur = db.Column(db.String(255))
    resume = db.Column(db.Text)
    date_publication = db.Column(db.Date)
    lien = db.Column(db.String(255))  # URL ou chemin vers l'article
    date_ajout = db.Column(db.Date, default=db.func.current_date())
    date_mise_a_jour = db.Column(db.Date, onupdate=db.func.current_date())
    
    # Relation avec les remèdes
    remedes = db.relationship('Remede', secondary='article_remede', back_populates='articles')
    # Relation avec les ingrédients
    ingredients = db.relationship('Ingredient', secondary='article_ingredient', back_populates='articles')



# Table de liaison entre Articles et Remèdes
class Article_Remede(db.Model):
    __tablename__ = 'article_remede'
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), primary_key=True)
    remede_id = db.Column(db.Integer, db.ForeignKey('remedes.id'), primary_key=True)

# Table de liaison entre Articles et Ingrédients
class Article_Ingredient(db.Model):
    __tablename__ = 'article_ingredient'
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.id'), primary_key=True)

# Table des Commentaires
class Commentaire(db.Model):
    __tablename__ = 'commentaires'
    id = db.Column(db.Integer, primary_key=True)
    like = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    remede_id = db.Column(db.Integer, db.ForeignKey('remedes.id'))
    comment = db.Column(db.String(255), nullable=False)
    date_ajout = db.Column(db.Date, default=db.func.current_date())
    date_mise_a_jour = db.Column(db.Date, onupdate=db.func.current_date())

    # Relations
    user = db.relationship('Users', backref='commentaires')
    remede = db.relationship('Remede', backref='commentaires')

# Table des Utilisateurs
class Users(db.Model, UserMixin):
    __tablename__ = 'Users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(64), unique=True)
    password = db.Column(db.LargeBinary)
    is_admin = db.Column(db.Boolean, default=False)
    date_inscription = db.Column(db.Date, default=date.today)

    # Relation avec Ingrédients et Remèdes
    ingredients = db.relationship('Ingredient', backref='user')
    remedes = db.relationship('Remede', backref='user')

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack its value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                value = value[0]

            if property == 'password':
                value = hash_pass(value)  # we need bytes here (not plain str)

            setattr(self, property, value)

    def __repr__(self):
        return f"<User {self.username}, Admin: {self.is_admin}>"

@login_manager.user_loader
def user_loader(id):
    return Users.query.filter_by(id=id).first()

@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = Users.query.filter_by(username=username).first()
    return user if user else None

