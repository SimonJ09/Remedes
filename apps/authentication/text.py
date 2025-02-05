
# -*- encoding: utf-8 -*-
from flask_login import UserMixin
from apps import db, login_manager
from datetime import date
from apps.authentication.util import hash_pass
# Table des Remèdes
class Articles(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    like = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    titre = db.Column(db.String(255), nullable=False)
    auteur = db.Column(db.Text)
    pdf = db.Column(db.String(255))
    doi = db.Column(db.String(255))
    liens = db.Column(db.String(255))  # Lien utile (ex: article ou source)
    date_ajout = db.Column(db.Date, default=db.func.current_date())
    date_mise_a_jour = db.Column(db.Date, onupdate=db.func.current_date())
    # Relation avec les ingrédients
    ingredients = db.relationship('RemedeIngredient', back_populates='articles')
    remedes = db.relationship('RemedeIngredient', back_populates='articles')
    __table_args__ = (
        db.UniqueConstraint('titre','auteur', name='unique_titre_auteur'),
    )
    ingredients = db.relationship('remede_ingredient_artciles', back_populates='articles')
   


# Table de liaison entre Remèdes et Ingrédients
class Remede_ingredient_artciles(db.Model):
    __tablename__ = 'remede_ingredient_articles'
    remede_id = db.Column(db.Integer, db.ForeignKey('remedes.id'), primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.id'), primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), primary_key=True)
    # Relations pour navigation
    remede = db.relationship('Remede', back_populates='articles')
    articles = db.relationship('Remede', back_populates='remede')
    ingredient = db.relationship('Ingredient', back_populates='articles')
    articles = db.relationship('Ingredient', back_populates='ingredient')
