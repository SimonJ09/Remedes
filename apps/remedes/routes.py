# -*- encoding: utf-8 -*-
from apps.remedes import blueprint

from flask import Flask
from flask import Flask

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
from apps.remedes.util import recherche_mot_cle , get_remedes_data
from sqlalchemy.orm import aliased
from sqlalchemy import or_


# Exemple d'utilisation dans une vue Flask


@blueprint.route('/remedes', methods=['GET', 'POST'])
@login_required
def remedes():
    is_admin = current_user.is_admin
    remedes = []  # Initialise la liste des remèdes
    mot_cle = request.form.get('mot_cle', "")  # Récupérer le mot-clé, vide par défaut
    page = int(request.args.get('page', 1))  # Page courante
    per_page = 10  # Nombre d'éléments par page

    if request.method == 'POST' and mot_cle:  # Si une recherche est effectuée
        # Appeler la fonction de recherche et traitement des résultats
        remedes_trouves = recherche_mot_cle(mot_cle)
        resultats = get_remedes_data(remedes_trouves)

        # Pagination
        total_remedes = len(resultats)
        total_pages = (total_remedes // per_page) + (1 if total_remedes % per_page > 0 else 0)
        resultats_pagination = resultats[(page - 1) * per_page:page * per_page]

        # Debugging pour vérifier les données
        print(f"Mot clé : {mot_cle}")
        print(f"Résultats trouvés ({len(resultats)}): {resultats_pagination}")

        # Passer les résultats au template
        return render_template(
            'remedes/menu.html',
            resultats=resultats_pagination,
            remedes=[],
            mot_cle=mot_cle,
            page=page,
            total_pages=total_pages,
            is_admin=is_admin,
        )

    # Si aucune recherche n'est effectuée (GET)
    if request.method == 'GET':
        # Charger tous les remèdes pour la page par défaut
        remedes = Remede.query.paginate(page=page, per_page=per_page, error_out=False)
        return render_template(
            'remedes/index.html',
            remedes=remedes.items,
            segment='index',
            is_admin=is_admin,
            mot_cle=mot_cle,
        )



from flask import render_template, request, redirect, url_for
from flask_login import login_required, current_user

@blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('authentication_blueprint.login'))


# Errors

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('home/page-404.html'), 404


@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('home/page-500.html'), 500
