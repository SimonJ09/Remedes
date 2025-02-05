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
from apps.authentication.models import Article_Ingredient, Article
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
            # Supprimer les liaisons dans d'autres tables si nécessaire (exemple : Articles, Ingredients, etc.)
            # Par exemple, si la maladie est liée à des articles :
            for article in mal.articles:
                db.session.delete(article)
            # Supprimer la maladie elle-même
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

@blueprint.route('/delete_selected_remede', methods=['GET','POST'])
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

        for remede in remedes_to_delete:
            # Suppression des liaisons avec les autres tables avant de supprimer le remède
            # Suppression des maladies associées
            for maladie in remede.maladies:
                remede.maladies.remove(maladie)

            # Suppression des articles associés
            for article in remede.articles:
                remede.articles.remove(article)

            # Suppression des ingrédients associés
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
    # Récupère la liste de tous les ingrédients pour alimenter ton formulaire
    all_ingredients = Ingredient.query.all()
    articles = Article.query.all()
    maux = Maladie.query.all()
    if form.validate_on_submit():
        try:
            # Gestion des fichiers image et vidéo
            image_file = request.files.get('images')
            filename_image = None
            if image_file:
                filename_image = save_file(image_file, subfolder="remedes")
                if not filename_image:
                    return render_template(
                        'admin/ajout_remede.html',
                        msg='Format de fichier image non valide.',
                        form=form, ingredients=all_ingredients,  maux =  maux, articles = articles
                    )

            video_file = request.files.get('video')
            filename_video = None
            if video_file:
                filename_video = save_file(video_file, subfolder="remedes")
                if not filename_video:
                    return render_template(
                        'admin/ajout_remede.html',
                        msg='Format de fichier vidéo non valide.',
                        form=form, ingredients=all_ingredients,  maux =  maux , articles = articles
                    )

            # Récupérer et convertir les données JSON des ingrédients sélectionnés
            ingredients_json = request.form.get('ingredients')
            selected_ingredients = []
            if ingredients_json:
                selected_ingredients = json.loads(ingredients_json)
                if not selected_ingredients:
                    return render_template(
                        'admin/ajout_remede.html',
                        msg='Ingrédients non sélectionnés.',
                        form=form, ingredients=all_ingredients,  maux=  maux , articles = articles
                    )
                
                
                
            articles_json = request.form.get('articles')
            selected_articles = []
            if articles_json:
                selected_articles = json.loads(articles_json)
                if not selected_articles :
                    return render_template(
                        'admin/ajout_remede.html',
                        msg='articles non sélectionnés.',
                        form=form, ingredients=all_ingredients ,  maux = maux , articles = articles
                    )
                
            maux_json = request.form.get('maux')
            selected_maux = []
            if maux_json:
                selected_maux = json.loads(maux_json)
                if not selected_maux:
                    return render_template(
                        'admin/ajout_remede.html',
                        msg='maux non sélectionnés.',
                        form=form, ingredients=all_ingredients ,  maux=  maux , articles = articles
                    )            
            
           
            # Créer le remède
            new_remede = Remede(
                nom=form.nom.data,
                description=form.description.data,
                preparation=form.preparation.data,
                latitude=form.latitude.data,
                longitude=form.longitude.data,
                indications=form.indications.data,
                dosage=form.dosage.data,
                precautions=form.precautions.data,
                video=filename_video,
                images=filename_image,
                liens=form.liens.data,
                user_id=current_user.id
            )
            
            db.session.add(new_remede)
            db.session.commit()  # Commit pour générer l'ID du remède

            # Ajouter les ingrédients sélectionnés au remède
            for ing_data in selected_ingredients:
                # Récupère l'ID et la quantité depuis l'objet JSON
                ingredient_id = ing_data.get('id')
                quantity = ing_data.get('quantity')
                
                # Vérifie que l'ingrédient existe
                ingredient = Ingredient.query.get(ingredient_id)
                if ingredient:
                    remede_ingredient = RemedeIngredient(
                        remede_id=new_remede.id,
                        ingredient_id=ingredient.id,
                        quantite=quantity
                    )
                    db.session.add(remede_ingredient)


            for ing_data in selected_articles:
                # Récupère l'ID et la quantité depuis l'objet JSON
                article_id = ing_data.get('id')
                # Vérifie que l'ingrédient existe
                article = Article.query.get(article_id)
                if article:
                    article_remede = Article_Remede(
                        remede_id=new_remede.id,
                        article_id = article.id,
                    )
                    db.session.add(article_remede)

            for ing_data in selected_maux :
                # Récupère l'ID et la quantité depuis l'objet JSON
                mal_id = ing_data.get('id')
                # Vérifie que l'ingrédient existe
                mal = Maladie.query.get(mal_id)
                if mal:
                    remedes_maladie = RemedeMaladie(
                        remede_id=new_remede.id,
                        maladie_id =  mal_id
                    )
                    db.session.add(remedes_maladie)

            db.session.commit()  # Commit final pour enregistrer les associations

            # Message de succès et retour sur la page d'ajout
            return render_template(
                'admin/ajout_remede.html',
                msg='Remède ajouté avec succès !',
                form=form,
                ingredients=all_ingredients ,  maux = maux , articles = articles
            )

        except IntegrityError:
            db.session.rollback()
            return render_template(
                'admin/ajout_remede.html',
                msg="Le remède existe déjà. Veuillez vérifier les informations.",
                form=form,
                ingredients=all_ingredients , maux =  maux, articles = articles
            )

        except Exception as e:
            db.session.rollback()
            return render_template(
                'admin/ajout_remede.html',
                msg=f"Une erreur s'est produite : {str(e)}",
                form=form,
                ingredients=all_ingredients , maux = maux ,articles = articles
            )

    return render_template('admin/ajout_remede.html', form=form, ingredients=all_ingredients, maux = maux, articles = articles)


@blueprint.route('/editer_remede/<int:id>', methods=['GET', 'POST'])
@login_required
def editer_remede(id):
    # Récupérer le remède existant
    remede = Remede.query.get_or_404(id)
    form = RemedeForm(obj=remede)

    # Récupère la liste de tous les ingrédients, articles et maladies pour alimenter le formulaire
    all_ingredients = Ingredient.query.all()
    articles = Article.query.all()
    maux = Maladie.query.all()

    # Pré-sélectionner les ingrédients, articles et maladies associés au remède
    selected_ingredients = [ri.ingredient_id for ri in remede.ingredients]
    selected_articles = [ar.article_id for ar in remede.articles]
    selected_maux = [rm.mal_id for rm in remede.maladie]

    if form.validate_on_submit():
        try:
            # Gestion des fichiers image et vidéo
            image_file = request.files.get('images')
            filename_image = remede.images  # Garde l'image actuelle si aucune nouvelle image n'est téléchargée
            if image_file:
                filename_image = save_file(image_file, subfolder="remedes")
                if not filename_image:
                    return render_template(
                        'admin/edit_remede.html',
                        msg='Format de fichier image non valide.',
                        form=form, remede=remede, ingredients=all_ingredients, maux=maux, articles=articles
                    )

            video_file = request.files.get('video')
            filename_video = remede.video  # Garde la vidéo actuelle si aucune nouvelle vidéo n'est téléchargée
            if video_file:
                filename_video = save_file(video_file, subfolder="remedes")
                if not filename_video:
                    return render_template(
                        'admin/edit_remede.html',
                        msg='Format de fichier vidéo non valide.',
                        form=form, remede=remede, ingredients=all_ingredients, maux=maux, articles=articles
                    )

            # Récupérer et convertir les données JSON des ingrédients, articles et maux sélectionnés
            ingredients_json = request.form.get('ingredients')
            selected_ingredients = []
            if ingredients_json:
                selected_ingredients = json.loads(ingredients_json)

            articles_json = request.form.get('articles')
            selected_articles = []
            if articles_json:
                selected_articles = json.loads(articles_json)

            maux_json = request.form.get('maux')
            selected_maux = []
            if maux_json:
                selected_maux = json.loads(maux_json)

            # Mettre à jour les informations du remède
            remede.nom = form.nom.data
            remede.description = form.description.data
            remede.preparation = form.preparation.data
            remede.latitude = form.latitude.data
            remede.longitude = form.longitude.data
            remede.indications = form.indications.data
            remede.dosage = form.dosage.data
            remede.precautions = form.precautions.data
            remede.video = filename_video
            remede.images = filename_image
            remede.liens = form.liens.data

            db.session.commit()  # Commit pour mettre à jour le remède

            # Mettre à jour les ingrédients associés
            RemedeIngredient.query.filter(RemedeIngredient.remede_id == remede.id).delete()  # Supprimer les anciens liens
            for ing_id in selected_ingredients:
                ingredient = Ingredient.query.get(ing_id)
                if ingredient:
                    remede_ingredient = RemedeIngredient(remede_id=remede.id, ingredient_id=ingredient.id)
                    db.session.add(remede_ingredient)

            # Mettre à jour les articles associés
            Article_Remede.query.filter(Article_Remede.remede_id == remede.id).delete()  # Supprimer les anciens liens
            for ar_id in selected_articles:
                article = Article.query.get(ar_id)
                if article:
                    article_remede = Article_Remede(remede_id=remede.id, article_id=article.id)
                    db.session.add(article_remede)

            # Mettre à jour les maladies associées
            RemedeMaladie.query.filter(RemedeMaladie.remede_id == remede.id).delete()  # Supprimer les anciens liens
            for mal_id in selected_maux:
                mal = Maladie.query.get(mal_id)
                if mal:
                    remedes_maladie = RemedeMaladie(remede_id=remede.id, mal_id=mal.id)
                    db.session.add(remedes_maladie)

            db.session.commit()  # Commit final pour enregistrer toutes les associations

            # Message de succès et retour sur la page d'édition
            return render_template(
                'admin/edit_remede.html',
                msg='Remède modifié avec succès !',
                form=form,
                remede=remede,
                ingredients=all_ingredients,
                maux=maux,
                articles=articles
            )

        except IntegrityError:
            db.session.rollback()
            return render_template(
                'admin/edit_remede.html',
                msg="Le remède existe déjà. Veuillez vérifier les informations.",
                form=form,
                remede=remede,
                ingredients=all_ingredients,
                maux=maux,
                articles=articles
            )

        except Exception as e:
            db.session.rollback()
            return render_template(
                'admin/edit_remede.html',
                msg=f"Une erreur s'est produite : {str(e)}",
                form=form,
                remede=remede,
                ingredients=all_ingredients,
                maux=maux,
                articles=articles
            )

    return render_template(
        'admin/edit_remede.html', 
        form=form, 
        remede=remede, 
        ingredients=all_ingredients, 
        maux=maux, 
        articles=articles
    )


@blueprint.route('/delete_remede/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_remede(id):
    # Récupérer le remède existant
    remede = Remede.query.get_or_404(id)

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
            'admin/remedes.html',  # Tu peux rediriger vers une page avec la liste des remèdes
            msg='Le remède a été supprimé avec succès !'
        )

    except Exception as e:
        db.session.rollback()  # Annuler la transaction en cas d'erreur
        return render_template(
            'admin/remedes.html',  # Rediriger vers la page des remèdes
            msg=f"Une erreur s'est produite lors de la suppression du remède : {str(e)}"
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
