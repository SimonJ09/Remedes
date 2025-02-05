# -*- encoding: utf-8 -*-
from apps.remedes import blueprint

from flask import render_template, request
from flask_login import login_required
from jinja2 import TemplateNotFound
from apps import db, login_manager
from apps.authentication.models import Users
from apps.authentication.models import Maladie
from apps.authentication.models import Ingredient
from apps.authentication.models import Remede
from apps.authentication.models import RemedeIngredient
from apps.authentication.models import Article_Ingredient, Article
from apps.authentication.models import Article_Remede
from apps.authentication.models import RemedeMaladie
from apps.admin.forms import IngredientForm
from apps.admin.forms import RemedeForm , ArticleForm
from datetime import datetime
from flask import render_template, redirect, request, url_for, jsonify , flash
from apps.admin.util import save_file
from flask_login import (
    current_user,
    login_user,
    logout_user
)

from sqlalchemy.orm import aliased
from sqlalchemy import or_

from sqlalchemy import or_

def recherche_mot_cle(mot_cle):
    # Normalisation du mot-clé pour éviter des erreurs avec des valeurs nulles ou invalides
    mot_cle = mot_cle.strip() if mot_cle else ""
    if not mot_cle:
        return []

    # Recherche dans la table des Maladies
    maladies_trouvees = Maladie.query.filter(
        or_(
            Maladie.nom_commun.ilike(f"%{mot_cle}%"),
            Maladie.nom_fon.ilike(f"%{mot_cle}%"),
            Maladie.proprietes.ilike(f"%{mot_cle}%")
        )
    ).all()

    # Recherche dans la table des Ingrédients
    ingredients_trouves = Ingredient.query.filter(
        or_(
            Ingredient.nom_commun.ilike(f"%{mot_cle}%"),
            Ingredient.nom_fon.ilike(f"%{mot_cle}%"),
            Ingredient.nom_scientifique.ilike(f"%{mot_cle}%"),
            Ingredient.proprietes.ilike(f"%{mot_cle}%")
        )
    ).all()

    # Recherche dans la table des Remèdes
    remedes_trouves = Remede.query.filter(
        or_(
            Remede.nom.ilike(f"%{mot_cle}%"),
            Remede.description.ilike(f"%{mot_cle}%"),
            Remede.preparation.ilike(f"%{mot_cle}%"),
            Remede.indications.ilike(f"%{mot_cle}%"),
            Remede.dosage.ilike(f"%{mot_cle}%"),
            Remede.precautions.ilike(f"%{mot_cle}%"),
            Remede.liens.ilike(f"%{mot_cle}%")
        )
    ).all()

    # Collecter les remèdes associés aux maladies trouvées
    remedes_par_maladie = set()
    for maladie in maladies_trouvees:
        for relation in maladie.remedes:  # Assure-toi que `maladie.remedes` retourne des objets liés.
            remedes_par_maladie.add(relation.remede)

    # Collecter les remèdes associés aux ingrédients trouvés
    remedes_par_ingredient = set()
    for ingredient in ingredients_trouves:
        for relation in ingredient.remedes:  # Assure-toi que `ingredient.remedes` retourne des objets liés.
            remedes_par_ingredient.add(relation.remede)

    # Fusionner tous les remèdes trouvés en éliminant les doublons
    remedes_uniques = set(remedes_trouves) | remedes_par_maladie | remedes_par_ingredient

    return list(remedes_uniques)


def get_remedes_data(remedes):
    # Si la liste est vide, retourner une liste vide
    if not remedes:
        return []

    remedes_data = []
    for remede in remedes:
        remede_info = {
            "images": remede.images,
            "nom": remede.nom,
            "description": remede.description,
            "indications": remede.indications,
            "dosage": remede.dosage,
            "liens": remede.liens,
            "ingredients": [],
            "maladies": [],
            "articles": [],
            "commentaires": []
        }

        # Récupérer les ingrédients du remède
        for remedeIngredient in remede.ingredients:
            ingredient_info = {
                "nom_commun": remedeIngredient.ingredient.nom_commun,
                "quantite": remedeIngredient.quantite
            }
            remede_info["ingredients"].append(ingredient_info)

        # Récupérer les maladies associées au remède
        for remedeMaladie in remede.maladie:
            maladie_info = {
                "nom_commun": remedeMaladie.maladie.nom_commun
            }
            remede_info["maladies"].append(maladie_info)

        # Récupérer les articles associés au remède
        for article in remede.articles:
            article_info = {
                "titre": article.titre,
                "lien": article.lien
            }
            remede_info["articles"].append(article_info)

        # Récupérer les commentaires associés au remède
        for commentaire in remede.commentaires:
            commentaire_info = {
                "username": commentaire.user.username,
                "comment": commentaire.comment
            }
            remede_info["commentaires"].append(commentaire_info)
        
        remedes_data.append(remede_info)
    
    return remedes_data
