# -*- encoding: utf-8 -*-
from apps.home import blueprint
from apps.admin import blueprint
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
from apps.authentication.models import Article_Ingredient, Article , Commentaire
from apps.authentication.models import Article_Remede
from apps.authentication.models import RemedeMaladie
from apps.admin.forms import IngredientForm ,RemedeForm , ArticleForm
from datetime import datetime
from flask import render_template, redirect, request, url_for, jsonify , flash
from apps.admin.util import save_file
from flask_login import (
    current_user,
    login_user,
    logout_user
)
# ------------------------------admin-----------------------------


@blueprint.route('/admin', methods=['GET','POST'])
@login_required
def index():
    if not current_user.is_admin:
       return render_template('home/page-500.html'), 500 
    return render_template('admin/index.html', segment='index')

#----------------------------------------------------------------


# ------------------------------Comments-----------------------------

@blueprint.route('/comment', methods=['GET','POST'])
@login_required
def comment():
    comments = Commentaire.query.all()
    users = Users.query.all()
    if not current_user.is_admin:
       return render_template('home/page-500.html'), 500 
    return render_template('admin/commentaires.html', segment='index', comments  = comments , users = users )





@blueprint.route('/add_comment', methods=['GET', 'POST'])
@login_required
def add_comment():
    # Initialisation du formulaire
    form = MaladieForm()
    if form.validate_on_submit():
        # Création d'une nouvelle instance de Maladie
        new_maladie = Maladie(
            nom_commun=form.nom_commun.data,
            nom_fon=form.nom_fon.data,
            proprietes=form.proprietes.data
        )

        # Gestion de l'image (si une image est envoyée)
        if form.images.data:
            image_file = request.files.get('images')
            if image_file:
                filename = save_file(image_file, subfolder="maladies")
                maladie.images = filename  # Mise à jour de l'image
                new_maladie.images = filename 

        # Sauvegarde de la nouvelle maladie dans la base de données
        db.session.add(new_maladie)
        db.session.commit()

        flash("Nouvelle maladie ajoutée avec succès!", "success")
        return redirect(url_for('admin_blueprint.maladie'))  # Rediriger vers une page après l'ajout

    return render_template('admin/ajout_maladie.html', form=form)


@blueprint.route('/edit_comment/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_comment(id):
    # Récupérer la maladie à partir de l'ID
    maladie = Maladie.query.get_or_404(id)

    # Initialiser le formulaire avec les données existantes
    form = MaladieForm(obj=maladie)

    if form.validate_on_submit():
        # Enregistrer l'image uploadée si elle existe
        image_file = request.files.get('images')
        if image_file:
            filename = save_file(image_file, subfolder="maladies")
            maladie.images = filename  # Mise à jour de l'image

        # Mettre à jour les autres champs
        maladie.nom_commun = form.nom_commun.data
        maladie.nom_fon = form.nom_fon.data
        maladie.proprietes = form.proprietes.data

        try:
            # Commit les modifications à la base de données
            db.session.commit()
            msg = "Maladie modifiée avec succès !"
            return render_template('admin/ajout_maladie.html', msg=msg, form=form)
        except Exception as e:
            db.session.rollback()
            msg = f"Une erreur s'est produite : {str(e)}"
            return render_template('admin/ajout_maladie.html', msg=msg, form=form)

    # Si le formulaire n'est pas soumis ou qu'il y a une erreur, retourner le formulaire avec les données préremplies
    return render_template('admin/ajout_maladie.html', form=form)


@blueprint.route('/delete_comment/<int:id>', methods=['POST'])
@login_required
def delete_comment(id):
    # Récupérer la maladie par ID
    maladie = Maladie.query.get_or_404(id)
    try:
        # Supprimer la maladie de la base de données
        db.session.delete(maladie)
        db.session.commit()
        flash("Maladie supprimée avec succès !", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Une erreur s'est produite lors de la suppression : {str(e)}", "danger")

    # Rediriger vers une page appropriée (par exemple, la liste des maladies)
    return redirect(url_for('admin_blueprint.dashboard_maladies'))


@blueprint.route('/delete_selected_comment', methods=['POST'])
@login_required
def delete_selected_comment():
    # Vérification des permissions d'accès (seulement les admins peuvent supprimer des maux)
    if not current_user.is_admin:
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('admin_blueprint.dashboard_maux'))

    # Récupérer les ID des maux à supprimer (envoyés via la requête JSON)
    ids = request.json.get('ids', [])
    if not ids:
        return jsonify({'success': False, 'message': "Aucun ID spécifié."}), 400

    try:
        # Récupérer les objets Maladie à partir des IDs
        maux_to_delete = Maladie.query.filter(Maladie.id.in_(ids)).all()
        for mal in maux_to_delete:
            db.session.delete(mal)
        # Commit les changements dans la base de données
        db.session.commit()
        return jsonify({'success': True, 'message': f"{len(maux_to_delete)} mal(s) supprimé(s) avec succès."})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f"Erreur : {str(e)}"}), 500


#--------------------------------------------------------------------
#--------------------------------------------------------------------







# ------------------------------user-----------------------------
#----------------------------------------------------------------

@blueprint.route('/user', methods=['GET','POST'])
@login_required
def user():
    users = Users.query.all()
    if not current_user.is_admin:
       return render_template('home/page-500.html'), 500 
    return render_template('admin/user-admin.html', users=users)



@blueprint.route('/toggle', methods=['POST'])
@login_required
def toggle_switch():
    # Récupérer les données de la requête
    data = request.get_json()
    toggle_id = data.get('id')
    if not toggle_id:
        return jsonify({'success': False, 'message': "ID utilisateur manquant."}), 400

    user = Users.query.filter_by(id=toggle_id).first()
    if not user:
        return jsonify({'success': False, 'message': "Utilisateur introuvable."}), 404

    status = data.get('status')  # True ou False
    if status is None:
        return jsonify({'success': False, 'message': "État manquant."}), 400

    # Appliquer une logique en fonction de l'état du toggle
    try:
        user.is_admin = bool(status)
        db.session.commit()
        message = f"{user.username} est maintenant admin." if status else f"{user.username} n'est plus admin."
        return jsonify({'success': True, 'message': message})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f"Erreur : {str(e)}"}), 500


@blueprint.route('/activate_selected_users', methods=['POST','GET'])
@login_required
def activate_selected_users():
    # Vérification des permissions d'accès
    if not current_user.is_admin:
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('admin_blueprint.dashboard_users'))

    ids = request.json.get('ids', [])
    if not ids:
        return jsonify({'success': False, 'message': "Aucun ID spécifié."}), 400

    try:
        users_to_activate = Users.query.filter(Users.id.in_(ids)).all()
        for user in users_to_activate:
            user.is_admin = True
        db.session.commit()
        return jsonify({'success': True, 'message': f"{len(users_to_activate)} utilisateur(s) activé(s) avec succès."})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f"Erreur : {str(e)}"}), 500


@blueprint.route('/deactivate_selected_users', methods=['POST','GET'])
@login_required
def deactivate_selected_users():
    # Vérification des permissions d'accès
    if not current_user.is_admin:
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('admin_blueprint.dashboard_users'))

    ids = request.json.get('ids', [])
    if not ids:
        return jsonify({'success': False, 'message': "Aucun ID spécifié."}), 400

    try:
        users_to_deactivate = Users.query.filter(Users.id.in_(ids)).all()
        for user in users_to_deactivate:
            user.is_admin = False
        db.session.commit()
        return jsonify({'success': True, 'message': f"{len(users_to_deactivate)} utilisateur(s) désactivé(s) avec succès."})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f"Erreur : {str(e)}"}), 500



@blueprint.route('/delete_user/<int:id>', methods=['GET'])
@login_required
def delete_user(id):
    # Vérification des permissions d'accès
    if not current_user.is_admin:
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('admin_blueprint.user'))

    # Récupérer l'utilisateur à supprimer
    user = Users.query.get_or_404(id)
    try:
        # Empêcher la suppression de l'utilisateur actuel
        if user == current_user:
            flash("Vous ne pouvez pas vous supprimer vous-même.", "warning")
            return redirect(url_for('admin_blueprint.user'))
        db.session.delete(user)
        db.session.commit()
        flash("Utilisateur supprimé avec succès !", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Une erreur s'est produite : {str(e)}", "danger")

    return redirect(url_for('admin_blueprint.user'))
#----------------------------------------------------------------


# ------------------------------maladie-----------------------------
#----------------------------------------------------------------

@blueprint.route('/maladie', methods=['GET','POST'])
@login_required
def maladie():
    maux = Maladie.query.all()
    users = Users.query.all()
    if not current_user.is_admin:
       return render_template('home/page-500.html'), 500 
    return render_template('admin/maladie.html', segment='index', maux = maux, users = users )


from .forms import MaladieForm

@blueprint.route('/add_maladie', methods=['GET', 'POST'])
@login_required
def add_maladie():
    # Initialisation du formulaire
    form = MaladieForm()
    if form.validate_on_submit():
        # Création d'une nouvelle instance de Maladie
        new_maladie = Maladie(
            nom_commun=form.nom_commun.data,
            nom_fon=form.nom_fon.data,
            proprietes=form.proprietes.data
        )

        # Gestion de l'image (si une image est envoyée)
        if form.images.data:
            image_file = request.files.get('images')
            if image_file:
                filename = save_file(image_file, subfolder="maladies")
                maladie.images = filename  # Mise à jour de l'image
                new_maladie.images = filename 

        # Sauvegarde de la nouvelle maladie dans la base de données
        db.session.add(new_maladie)
        db.session.commit()

        flash("Nouvelle maladie ajoutée avec succès!", "success")
        return redirect(url_for('admin_blueprint.maladie'))  # Rediriger vers une page après l'ajout

    return render_template('admin/ajout_maladie.html', form=form)


@blueprint.route('/edit_maladie/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_maladie(id):
    # Récupérer la maladie à partir de l'ID
    maladie = Maladie.query.get_or_404(id)

    # Initialiser le formulaire avec les données existantes
    form = MaladieForm(obj=maladie)

    if form.validate_on_submit():
        # Enregistrer l'image uploadée si elle existe
        image_file = request.files.get('images')
        if image_file:
            filename = save_file(image_file, subfolder="maladies")
            maladie.images = filename  # Mise à jour de l'image

        # Mettre à jour les autres champs
        maladie.nom_commun = form.nom_commun.data
        maladie.nom_fon = form.nom_fon.data
        maladie.proprietes = form.proprietes.data

        try:
            # Commit les modifications à la base de données
            db.session.commit()
            msg = "Maladie modifiée avec succès !"
            return render_template('admin/ajout_maladie.html', msg=msg, form=form)
        except Exception as e:
            db.session.rollback()
            msg = f"Une erreur s'est produite : {str(e)}"
            return render_template('admin/ajout_maladie.html', msg=msg, form=form)

    # Si le formulaire n'est pas soumis ou qu'il y a une erreur, retourner le formulaire avec les données préremplies
    return render_template('admin/ajout_maladie.html', form=form)


@blueprint.route('/delete_maladie/<int:id>', methods=['POST'])
@login_required
def delete_maladie(id):
    # Récupérer la maladie par ID
    maladie = Maladie.query.get_or_404(id)
    try:
        # Supprimer la maladie de la base de données
        db.session.delete(maladie)
        db.session.commit()
        flash("Maladie supprimée avec succès !", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Une erreur s'est produite lors de la suppression : {str(e)}", "danger")

    # Rediriger vers une page appropriée (par exemple, la liste des maladies)
    return redirect(url_for('admin_blueprint.dashboard_maladies'))


@blueprint.route('/delete_selected_maux', methods=['POST'])
@login_required
def delete_selected_maux():
    # Vérification des permissions d'accès (seulement les admins peuvent supprimer des maux)
    if not current_user.is_admin:
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('admin_blueprint.dashboard_maux'))

    # Récupérer les ID des maux à supprimer (envoyés via la requête JSON)
    ids = request.json.get('ids', [])
    if not ids:
        return jsonify({'success': False, 'message': "Aucun ID spécifié."}), 400

    try:
        # Récupérer les objets Maladie à partir des IDs
        maux_to_delete = Maladie.query.filter(Maladie.id.in_(ids)).all()
        for mal in maux_to_delete:
            db.session.delete(mal)
        # Commit les changements dans la base de données
        db.session.commit()
        return jsonify({'success': True, 'message': f"{len(maux_to_delete)} mal(s) supprimé(s) avec succès."})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f"Erreur : {str(e)}"}), 500

#----------------------------------------------------------------

# ------------------------------Article-----------------------------
#----------------------------------------------------------------

@blueprint.route('/article', methods=['GET','POST'])
@login_required
def article():
    articles = Article.query.all()
    users = Users.query.all()
    if not current_user.is_admin:
       return render_template('home/page-500.html'), 500 
    return render_template('admin/article.html', segment='index', articles = articles, users = users )

@blueprint.route('/ajout_article', methods=['GET', 'POST'])
@login_required
def ajout_article():
    form = ArticleForm()
    if request.method == 'POST':
        titre = request.form.get('titre')
        auteur = request.form.get('auteur')
        resume = request.form.get('resume')
        date_str = request.form.get('date_publication')
        date_publication = datetime.strptime(date_str, '%Y-%m-%d').date()
        lien = request.form.get('lien')
        # Créer un nouvel article
        new_article = Article(
            titre=titre,
            auteur=auteur,
            resume=resume,
            date_publication=date_publication,
            lien=lien
        )

        try:
            # Ajouter l'article à la base de données
            db.session.add(new_article)
            db.session.commit()
            flash("Article ajouté avec succès!", "success")
            return redirect(url_for('admin_blueprint.article'))  # Redirection vers la liste des articles
        except Exception as e:
            db.session.rollback()
            flash(f"Erreur lors de l'ajout de l'article : {str(e)}", "danger")
            return redirect(url_for('admin_blueprint.ajout_article'))

    return render_template('admin/ajout_article.html', form = form)  # Retourne le formulaire d'ajout d'article

@blueprint.route('/edit_article/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_article(id):
    form = ArticleForm()
    article = Article.query.get_or_404(id)  # Récupérer l'article à éditer
    if request.method == 'POST':
        article.titre = request.form.get('titre')
        article.auteur = request.form.get('auteur')
        article.resume = request.form.get('resume')
        article.date_publication = request.form.get('date_publication')
        article.lien = request.form.get('lien')

        try:
            # Sauvegarder les changements dans la base de données
            db.session.commit()
            flash("Article modifié avec succès!", "success")
            return redirect(url_for('admin_blueprint.article'))  # Redirection vers la liste des articles
        except Exception as e:
            db.session.rollback()
            flash(f"Erreur lors de la modification de l'article : {str(e)}", "danger")
            return redirect(url_for('admin_blueprint.edit_article', id=id))
    else:
    # Pré-remplir le formulaire avec les données existantes si on est en mode GET
        form.titre.data = article.titre
        form.auteur.data = article.auteur
        form.resume.data = article.resume
        form.date_publication.data = article.date_publication
        form.lien.data = article.lien

    return render_template('admin/edit_article.html', article=article, form = form)  # Retourne le formulaire d'édition d'article




@blueprint.route('/delete_article/<int:id>', methods=['POST','GET'])
@login_required
def delete_article(id):
    article = Article.query.get_or_404(id)  # Récupérer l'article à supprimer
    try:
        print(article)
        db.session.delete(article)  # Supprimer l'article
        db.session.commit()
        flash("Article supprimé avec succès!", "success")
        return redirect(url_for('admin_blueprint.article'))  # Redirection vers la liste des articles
    except Exception as e:
        db.session.rollback()
        flash(f"Erreur lors de la suppression de l'article : {str(e)}", "danger")
        return redirect(url_for('admin_blueprint.article'))

@blueprint.route('/delete_selected_articles', methods=['POST'])
@login_required
def delete_selected_articles():
    # Vérification des permissions d'accès
    if not current_user.is_admin:
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('admin_blueprint.dashboard_articles'))

    ids = request.json.get('ids', [])
    if not ids:
        return jsonify({'success': False, 'message': "Aucun ID spécifié."}), 400

    try:
        articles_to_delete = Article.query.filter(Article.id.in_(ids)).all()

        # Supprimer les articles récupérés
        for article in articles_to_delete:
            db.session.delete(article)

        # Commit les changements
        db.session.commit()

        return jsonify({'success': True, 'message': f"{len(articles_to_delete)} article(s) supprimé(s) avec succès."})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f"Erreur : {str(e)}"}), 500

#----------------------------------------------------------------


# ------------------------------remedes-----------------------------
#----------------------------------------------------------------

@blueprint.route('/delete_selected_remede', methods=['GET', 'POST'])
@login_required
def delete_selected_remede():
    # Vérification des permissions d'accès
    if not current_user.is_admin:
        flash("Accès non autorisé.", "danger")
        return redirect(url_for('admin_blueprint.dashboard_remedes'))

    ids = request.json.get('ids', [])
    if not ids:
        return jsonify({'success': False, 'message': "Aucun ID spécifié."}), 400

    try:
        remedes_to_delete = Remede.query.filter(Remede.id.in_(ids)).all()

        if not remedes_to_delete:
            return jsonify({'success': False, 'message': "Aucun remède trouvé avec ces IDs."}), 404

        for remede in remedes_to_delete:
            # Suppression des partages associés
            if hasattr(remede, 'partages') and remede.partages:
                for partage in remede.partages:
                    db.session.delete(partage)

            # Suppression des likes associés
            if hasattr(remede, 'likes') and remede.likes:
                for like in remede.likes:
                    db.session.delete(like)
                    

            # Suppression des commentaires associés
            if hasattr(remede, 'commentaires') and remede.commentaires:
                for commentaire in remede.commentaires:
                    db.session.delete(commentaire)


            # Suppression des maladies associées
            if hasattr(remede, 'maladie') and remede.maladie:
                for remede_maladie in remede.maladie:
                    remede.maladie.remove(remede_maladie.maladie)

            # Suppression des articles associés
            if hasattr(remede, 'articles') and remede.articles:
                for article in remede.articles:
                    remede.articles.remove(article)
                
            # Suppression des ingrédients associés
            if hasattr(remede, 'ingredients') and remede.ingredients:
                for ingredient in remede.ingredients:
                    remede.ingredients.remove(ingredient)
                    

            # Suppression du remède lui-même
            db.session.delete(remede)

        db.session.commit()
        return jsonify({'success': True, 'message': f"{len(remedes_to_delete)} remède(s) supprimé(s) avec succès."})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f"Erreur : {str(e)}"}), 500


@blueprint.route('/dashboard_remede')
@login_required
def dashboard_remede():
    remedes = Remede.query.all()
    if not current_user.is_admin:
        return render_template('home/page-500.html'), 500 
    return render_template('admin/remede_list.html', remedes=remedes)

from sqlalchemy.exc import IntegrityError
import json

@blueprint.route('/ajout_remede', methods=['GET', 'POST'])
@login_required
def ajout_remede():
    form = RemedeForm()
    # Récupération de tous les ingrédients, articles et maux
    try:
        all_ingredients = Ingredient.query.all()
        articles = Article.query.all()
        maux = Maladie.query.all()
    except Exception as e:
        return f"Erreur lors de la récupération des données initiales : {str(e)}"

    if form.validate_on_submit():
        try:
            # Gestion des fichiers image
            try:
                image_file = request.files.get('images')
                filename_image = None
                if image_file:
                    filename_image = save_file(image_file, subfolder="remedes")
                    if not filename_image:
                        return render_template(
                            'admin/ajout_remede.html',
                            msg='Format de fichier image non valide.',
                            form=form, ingredients=all_ingredients, maux=maux, articles=articles
                        )
            except Exception as e:
                return f"Erreur lors du traitement de l'image : {str(e)}"

            # Gestion des fichiers vidéo
            try:
                video_file = request.files.get('video')
                filename_video = None
                if video_file:
                    filename_video = save_file(video_file, subfolder="remedes")
                    if not filename_video:
                        return render_template(
                            'admin/ajout_remede.html',
                            msg='Format de fichier vidéo non valide.',
                            form=form, ingredients=all_ingredients, maux=maux, articles=articles
                        )
            except Exception as e:
                return f"Erreur lors du traitement de la vidéo : {str(e)}"

            # Traitement des ingrédients sélectionnés
            try:
                ingredients_json = request.form.get('ingredients')
                selected_ingredients = []
                if ingredients_json:
                    selected_ingredients = json.loads(ingredients_json)
                    if not selected_ingredients:
                        return render_template(
                            'admin/ajout_remede.html',
                            msg='Ingrédients non sélectionnés.',
                            form=form, ingredients=all_ingredients, maux=maux, articles=articles
                        )
            except Exception as e:
                return f"Erreur lors du traitement des ingrédients : {str(e)}"

            # Traitement des articles sélectionnés
            try:
                articles_json = request.form.get('articles')
                selected_articles = []
                if articles_json:
                    selected_articles = json.loads(articles_json)
                    if not selected_articles:
                        return render_template(
                            'admin/ajout_remede.html',
                            msg='Articles non sélectionnés.',
                            form=form, ingredients=all_ingredients, maux=maux, articles=articles
                        )
            except Exception as e:
                return f"Erreur lors du traitement des articles : {str(e)}"

            # Traitement des maux sélectionnés
            try:
                maux_json = request.form.get('maux')
                selected_maux = []
                if maux_json:
                    selected_maux = json.loads(maux_json)
                    if not selected_maux:
                        return render_template(
                            'admin/ajout_remede.html',
                            msg='Maux non sélectionnés.',
                            form=form, ingredients=all_ingredients, maux=maux, articles=articles
                        )
            except Exception as e:
                return f"Erreur lors du traitement des maux : {str(e)}"

            # Création du remède
            try:
                new_remede = Remede(
                    nom=form.nom.data,
                    description=form.description.data,
                    preparation=form.preparation.data,
                    latitude=form.latitude.data,
                    longitude=form.longitude.data,
                    indications=form.indications.data,
                    posologie =form.posologie.data,
                    precautions=form.precautions.data,
                    video=filename_video,
                    images=filename_image,
                    liens=form.liens.data,
                    user_id=current_user.id
                )
                db.session.add(new_remede)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                return f"Erreur lors de la création du remède : {str(e)}"

            # Ajout des ingrédients au remède
            try:
                for ing_data in selected_ingredients:
                    ingredient_id = ing_data.get('id')
                    quantity = ing_data.get('quantity')
                    ingredient = Ingredient.query.get(ingredient_id)
                    if ingredient:
                        remede_ingredient = RemedeIngredient(
                            remede_id=new_remede.id,
                            ingredient_id=ingredient.id,
                            quantite=quantity
                        )
                        db.session.add(remede_ingredient)
            except Exception as e:
                db.session.rollback()
                return f"Erreur lors de l'association des ingrédients : {str(e)}"

            # Ajout des articles au remède
            try:
                for art_data in selected_articles:
                    article_id = art_data.get('id')
                    article = Article.query.get(article_id)
                    if article:
                        article_remede = Article_Remede(
                            remede_id=new_remede.id,
                            article_id = article.id,
                        )
                        db.session.add(article_remede)
            except Exception as e:
                db.session.rollback()
                return f"Erreur lors de l'association des articles : {str(e)}"

            # Ajout des maux au remède
            try:
                for mal_data in selected_maux:
                    mal_id = mal_data.get('id')
                    mal = Maladie.query.get(mal_id)
                    if mal:
                        remedes_maladie = RemedeMaladie(
                            remede_id=new_remede.id,
                            maladie_id=mal.id
                        )
                        db.session.add(remedes_maladie)
            except Exception as e:
                db.session.rollback()
                return f"Erreur lors de l'association des maux : {str(e)}"

            # Commit final
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                return f"Erreur lors du commit final : {str(e)}"

            # Retour au formulaire avec un message de succès
            return render_template(
                'admin/ajout_remede.html',
                msg='Remède ajouté avec succès !',
                form=form, ingredients=all_ingredients, maux=maux, articles=articles
            )

        except IntegrityError:
            db.session.rollback()
            return render_template(
                'admin/ajout_remede.html',
                msg="Le remède existe déjà. Veuillez vérifier les informations.",
                form=form, ingredients=all_ingredients, maux=maux, articles=articles
            )

        except Exception as e:
            db.session.rollback()
            return f"Erreur générale : {str(e)}"

    return render_template('admin/ajout_remede.html', form=form, ingredients=all_ingredients, maux=maux, articles=articles)

@blueprint.route('/edit_remede/<int:remede_id>', methods=['GET', 'POST'])
@login_required
def edit_remede(remede_id):
    # Récupération du remède par son ID
    remede = Remede.query.get_or_404(remede_id)
    # Préparation des données pour selected_ingredients
    selected_ingredients = remede.ingredients  # La relation 'ingredients' peut être vide

    selected_ingredients_data = [
        {
            "id": ingredient.id,
            "nom_commun": ingredient.nom_commun,  # Utilisation de 'nom_commun' au lieu de 'name' 
            "nom_scientifique": ingredient.nom_scientifique,  # Ajoute le nom scientifique si nécessaire
            "quantite": remede_ingredient.quantite  # La quantité spécifique dans ce remède
        }
        for remede_ingredient in selected_ingredients
        for ingredient in [remede_ingredient.ingredient]
    ] if selected_ingredients else []  # Si aucun ingrédient, renvoie une liste vide

    # Préparation des données pour selected_maux
    selected_maux = remede.maladie  # La relation 'maladie' peut aussi être vide

    selected_maux_data = [
        {
            "id": maladie.id,
            "nom_commun": maladie.nom_commun,  # Utilisation de 'nom_commun' et 'nom_fon' pour la maladie
            "nom_fon": maladie.nom_fon
        }
        for remede_maladie in selected_maux
        for maladie in [remede_maladie.maladie]
    ] if selected_maux else []  # Si aucune maladie, renvoie une liste vide

    # Préparation des données pour selected_articles
    selected_articles = remede.articles  # La relation 'articles' peut être vide

    selected_articles_data = [
        {
            "id": article.id,
            "titre": article.titre,  # Utilisation de 'titre' pour le titre de l'article
            "auteur": article.auteur,  # Ajoute l'auteur si nécessaire
            "resume": article.resume  # Résumé de l'article, si nécessaire
        }
        for article in selected_articles
    ] if selected_articles else []  # Si aucun article, renvoie une liste vide

    remede_data = {
        "nom": remede.nom,
        "description": remede.description,
        "preparation": remede.preparation,
        "latitude": remede.latitude,
        "longitude": remede.longitude,
        "indications": remede.indications,
        "posologie": remede.posologie ,
        "precautions": remede.precautions,
        "video": remede.video,
        "images": remede.images,
        "liens": remede.liens,
        # Assurez-vous que toutes les autres données nécessaires sont sérialisables
    }

    # Initialisation du formulaire
    form = RemedeForm(obj=remede)

    # Récupération des autres données nécessaires
    try:
        all_ingredients = Ingredient.query.all()
        articles = Article.query.all()
        maux = Maladie.query.all()
    except Exception as e:
        return f"Erreur lors de la récupération des données initiales : {str(e)}"

    # Si le formulaire est validé
    if form.validate_on_submit():
        try:
            # Gestion des fichiers image
            image_file = request.files.get('images')
            filename_image = remede.images  # Conserver l'image existante si aucune nouvelle n'est soumise
            if image_file:
                filename_image = save_file(image_file, subfolder="remedes")
                if not filename_image:
                    return render_template(
                        'admin/edit_remede.html',
                        msg='Format de fichier image non valide.',
                        form=form, remede=remede, ingredients=all_ingredients, maux=maux, articles=articles,  selected_ingredients=selected_ingredients_data,
    selected_maux=selected_maux_data,
    selected_articles=selected_articles_data
                    )

            # Gestion des fichiers vidéo
            video_file = request.files.get('video')
            filename_video = remede.video  # Conserver la vidéo existante si aucune nouvelle n'est soumise
            if video_file:
                filename_video = save_file(video_file, subfolder="remedes")
                if not filename_video:
                    return render_template(
                        'admin/edit_remede.html',
                        msg='Format de fichier vidéo non valide.',
                        form=form, remede=remede_data, ingredients=all_ingredients, maux=maux, articles=articles , selected_ingredients=selected_ingredients_data,
    selected_maux=selected_maux_data,
    selected_articles=selected_articles_data
                    )

            # Traitement des ingrédients sélectionnés
            ingredients_json = request.form.get('ingredients')
            selected_ingredients = []
            if ingredients_json:
                selected_ingredients = json.loads(ingredients_json)
                if not selected_ingredients:
                    return render_template(
                        'admin/edit_remede.html',
                        msg='Ingrédients non sélectionnés.',
                        form=form, remede=remede_data, ingredients=all_ingredients, maux=maux, articles=articles,  selected_ingredients=selected_ingredients_data,
    selected_maux=selected_maux_data,
    selected_articles=selected_articles_data
                    )

            # Traitement des articles sélectionnés
            articles_json = request.form.get('articles')
            selected_articles = []
            if articles_json:
                selected_articles = json.loads(articles_json)
                if not selected_articles:
                    return render_template(
                        'admin/edit_remede.html',
                        msg='Articles non sélectionnés.',
                        form=form, remede=remede_data, ingredients=all_ingredients, maux=maux, articles=articles ,  selected_ingredients=selected_ingredients_data,
    selected_maux=selected_maux_data,
    selected_articles=selected_articles_data
                    )

            # Traitement des maux sélectionnés
            maux_json = request.form.get('maux')
            selected_maux = []
            if maux_json:
                selected_maux = json.loads(maux_json)
                if not selected_maux:
                    return render_template(
                        'admin/edit_remede.html',
                        msg='Maux non sélectionnés.',
                        form=form, remede=remede_data, ingredients=all_ingredients, maux=maux, articles=articles ,  selected_ingredients=selected_ingredients_data,
    selected_maux=selected_maux_data,
    selected_articles=selected_articles_data
                    )

            # Mise à jour du remède
            remede.nom = form.nom.data
            remede.description = form.description.data
            remede.preparation = form.preparation.data
            remede.latitude = form.latitude.data
            remede.longitude = form.longitude.data
            remede.indications = form.indications.data
            remede.posologie = form.posologie.data
            remede.precautions = form.precautions.data
            remede.video = filename_video
            remede.images = filename_image
            remede.liens = form.liens.data

            db.session.commit()

            # Suppression des associations existantes (ingrédients, articles, maux)
            RemedeIngredient.query.filter_by(remede_id=remede.id).delete()
            Article_Remede.query.filter_by(remede_id=remede.id).delete()
            RemedeMaladie.query.filter_by(remede_id=remede.id).delete()

            # Ajout des nouvelles associations
            for ing_data in selected_ingredients:
                ingredient_id = ing_data.get('id')
                quantity = ing_data.get('quantity')
                ingredient = Ingredient.query.get(ingredient_id)
                if ingredient:
                    remede_ingredient = RemedeIngredient(
                        remede_id=remede.id,
                        ingredient_id=ingredient.id,
                        quantite=quantity
                    )
                    db.session.add(remede_ingredient)

            for art_data in selected_articles:
                article_id = art_data.get('id')
                article = Article.query.get(article_id)
                if article:
                    article_remede = Article_Remede(
                        remede_id=remede.id,
                        article_id=article.id,
                    )
                    db.session.add(article_remede)

            for mal_data in selected_maux:
                mal_id = mal_data.get('id')
                mal = Maladie.query.get(mal_id)
                if mal:
                    remedes_maladie = RemedeMaladie(
                        remede_id=remede.id,
                        maladie_id=mal.id
                    )
                    db.session.add(remedes_maladie)

            db.session.commit()

            return render_template(
                'admin/edit_remede.html',
                msg='Remède mis à jour avec succès !',
                form=form, remede=remede_data, ingredients=all_ingredients, maux=maux, articles=articles , selected_ingredients=selected_ingredients_data,
    selected_maux=selected_maux_data,
    selected_articles=selected_articles_data
            )

        except Exception as e:
            db.session.rollback()
            return f"Erreur lors de l'édition du remède : {str(e)}"

    return render_template('admin/edit_remede.html', form=form, remede=remede_data, ingredients=all_ingredients, maux=maux, articles=articles,  selected_ingredients=selected_ingredients_data,
    selected_maux=selected_maux_data,
    selected_articles=selected_articles_data)


@blueprint.route('/delete_remede/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_remede(id):
    # Récupérer le remède existant
    remede = Remede.query.get_or_404(id)
    remedes = Remede.query.all()
    try:
        # Supprimer les associations avec les ingrédients
        RemedeIngredient.query.filter(RemedeIngredient.remede_id == remede.id).delete()
        # Supprimer les associations avec les articles
        Article_Remede.query.filter(Article_Remede.remede_id == remede.id).delete()
        # Supprimer les associations avec les maladies
        RemedeMaladie.query.filter(RemedeMaladie.remede_id == remede.id).delete()
        # Supprimer le remède
        db.session.delete(remede)
        # Commit pour valider les suppressions
        db.session.commit()
        # Message de succès
        return render_template(
            'admin/remede_list.html',  # Tu peux rediriger vers une page avec la liste des remèdes
            message ='Le remède a été supprimé avec succès !',  remedes = remedes
        )
    except Exception as e:
        db.session.rollback()  # Annuler la transaction en cas d'erreur
        return render_template(
            'admin/remede_list.html',  # Rediriger vers la page des remèdes
            message =f"Une erreur s'est produite lors de la suppression du remède : {str(e)}" , remedes=remedes
        )

# ------------------------------Ingrédiant-----------------------------
@blueprint.route('/dashboard_ingredient', methods=['GET','POST'])
@login_required
def dashboard_ingredient():
    ingredients = Ingredient.query.all()
    if not current_user.is_admin:
        return render_template('home/page-500.html'), 500 
    return render_template('admin/ingredient_list.html', ingredients=ingredients)

from sqlalchemy.exc import IntegrityError

@blueprint.route('/add_ingredient', methods=['GET','POST'])
@login_required
def add_ingredient():
    form = IngredientForm()
    if form.validate_on_submit():
        try:
            # Gestion de l'image
            image_file = request.files.get('images')
            filename = None

            if image_file:
                filename = save_file(image_file, subfolder="ingredients")
                if not filename:
                    return render_template(
                        'admin/add_ingredient.html',
                        msg='Format de fichier non valide.',
                        form=form
                    )

            # Création de l'objet ingrédient
            new_ingredient = Ingredient(
                nom_commun=form.nom_commun.data,
                nom_fon=form.nom_fon.data,
                nom_scientifique=form.nom_scientifique.data,
                partie=form.partie.data,
                proprietes=form.proprietes.data,
                latitude=form.latitude.data,
                longitude=form.longitude.data,
                images=filename,
                like=form.like.data or 0,
                user_id=current_user.id
            )

            # Ajout et validation en base de données
            db.session.add(new_ingredient)
            db.session.commit()

            # Message de succès
            return render_template(
                'admin/add_ingredient.html',
                msg='Ingrédient ajouté avec succès !',
                form=form
            )

        except IntegrityError:
            db.session.rollback()
            return render_template(
                'admin/add_ingredient.html',
                msg=f"L'ingrédient avec le nom scientifique '{form.nom_scientifique.data}' et la partie '{form.partie.data}' existe déjà. Veuillez vérifier les informations ou essayer avec un autre nom.",
                form=form
            )

        except Exception as e:
            db.session.rollback()
            return render_template(
                'admin/add_ingredient.html',
                msg=(f"Une erreur s'est produite : {str(e)}", "danger"),
                form=form
            )

    # Cas GET ou formulaire non valide
    return render_template('admin/add_ingredient.html', form=form)

@blueprint.route('/ajout_ingredient', methods=['GET', 'POST'])
@login_required
def ajout_ingredient():
    form = IngredientForm()

    if form.validate_on_submit():
        try:
            # Gestion de l'image
            image_file = request.files.get('images')
            filename = None

            if image_file:
                filename = save_file(image_file, subfolder="ingredients")
                if not filename:
                    return render_template(
                        'admin/ajout_ingredient.html',
                        msg='Format de fichier non valide.',
                        form=form
                    )

            # Création de l'objet ingrédient
            new_ingredient = Ingredient(
                nom_commun=form.nom_commun.data,
                nom_fon=form.nom_fon.data,
                nom_scientifique=form.nom_scientifique.data,
                partie=form.partie.data,
                proprietes=form.proprietes.data,
                latitude=form.latitude.data,
                longitude=form.longitude.data,
                images=filename,
                like=form.like.data or 0,
                user_id=current_user.id
            )

            # Ajout et validation en base de données
            db.session.add(new_ingredient)
            db.session.commit()

            # Message de succès
            return render_template(
                'admin/ajout_ingredient.html',
                msg='Ingrédient ajouté avec succès !',
                form=form
            )

        except IntegrityError:
            db.session.rollback()
            return render_template(
                'admin/ajout_ingredient.html',
                msg=f"L'ingrédient avec le nom scientifique '{form.nom_scientifique.data}' et la partie '{form.partie.data}' existe déjà. Veuillez vérifier les informations ou essayer avec un autre nom.",
                form=form
            )

        except Exception as e:
            db.session.rollback()
            return render_template(
                'admin/ajout_ingredient.html',
                msg=(f"Une erreur s'est produite : {str(e)}", "danger"),
                form=form
            )

    # Cas GET ou formulaire non valide
    return render_template('admin/ajout_ingredient.html', form=form)

@blueprint.route('/edit_ingredient/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_ingredient(id):
    # Récupérer l'ingrédient à partir de l'ID
    ingredient = Ingredient.query.get_or_404(id)

    # Initialiser le formulaire avec les données existantes
    form = IngredientForm(obj=ingredient)

    if form.validate_on_submit():
        # Enregistrer l'image uploadée si elle existe
        image_file = request.files.get('images')
        if image_file:
            filename = save_file(image_file, subfolder="ingredients")
            ingredient.images = filename  # Mise à jour de l'image

        # Mettre à jour les autres champs
        ingredient.nom_commun = form.nom_commun.data
        ingredient.nom_fon = form.nom_fon.data
        ingredient.nom_scientifique = form.nom_scientifique.data
        ingredient.partie = form.partie.data
        ingredient.proprietes = form.proprietes.data
        ingredient.latitude = form.latitude.data
        ingredient.longitude = form.longitude.data
        ingredient.like = form.like.data or 0  # Défaut à 0 si non renseigné

        try:
            # Commit les modifications à la base de données
            db.session.commit()
            msg = "Ingrédient modifié avec succès !"
            return render_template('admin/ajout_ingredient.html', msg=msg, form=form)
        except Exception as e:
            db.session.rollback()
            msg = f"Une erreur s'est produite : {str(e)}"
            return render_template('admin/ajout_ingredient.html', msg=msg, form=form)

    # Si le formulaire n'est pas soumis ou qu'il y a une erreur, retourner le formulaire avec les données préremplies
    return render_template('admin/ajout_ingredient.html', form=form)

# Route pour supprimer les éléments sélectionnés
@blueprint.route('/delete_selected_ingredients', methods=['GET'])
def delete_selected_ingredients():
    ids = request.args.get('ids').split(',')
    ingredients_to_delete = Ingredient.query.filter(Ingredient.id.in_(ids)).all()
    for ingredient in ingredients_to_delete:
        db.session.delete(ingredient)
    db.session.commit()
    return render_template('admin/ingredient_list.html')

@blueprint.route('/delete_ingredient/<int:id>', methods=['GET'])
@login_required
def delete_ingredient(id):
    # Récupérer l'ingrédient à supprimer
    ingredient = Ingredient.query.get_or_404(id)

    try:
        db.session.delete(ingredient)
        db.session.commit()
        msg = "Ingrédient modifié avec succès !"
        return render_template('admin/ingredient_list.html', msg=msg)
    except Exception as e:
        db.session.rollback()
        msg = (f"Une erreur s'est produite : {str(e)}", "danger")
        return render_template('admin/ingredient_list.html', msg=msg)


# ------------------------------error-----------------------------

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
