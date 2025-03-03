# -*- encoding: utf-8 -*-


from flask import render_template, redirect, request, url_for
from flask_login import (
    current_user,
    login_user,
    logout_user
)

from apps import db, login_manager
from apps.authentication import blueprint
from apps.authentication.forms import LoginForm, CreateAccountForm
from apps.authentication.models import Users
from datetime import date
from apps.authentication.util import verify_pass, hash_pass


# Login & Registration

@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)
    if 'login' in request.form:
        # read form data
        username = request.form['username']
        password = request.form['password']
        # Locate user
        user = Users.query.filter_by(username=username).first()
        # Check the password
        if user and verify_pass(password, user.password):
            login_user(user)
            return redirect(url_for('remedes_blueprint.remedes'))

        # Something (user or pass) is not ok
        return render_template('accounts/login.html',
                               msg='Wrong user or password',
                               form=login_form)

    if not current_user.is_authenticated:
        return render_template('accounts/login.html',
                               form=login_form)
    return redirect(url_for('remedes_blueprint.index'))


@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    create_account_form = CreateAccountForm(request.form)
    if 'register' in request.form:

        username = request.form['username']
        email = request.form['email']
        
        # Check usename exists
        user = Users.query.filter_by(username=username).first()
        if user:
            return render_template('accounts/register.html',
                                   msg='Username already registered',
                                   success=False,
                                   form=create_account_form)

        # Check email exists
        user = Users.query.filter_by(email=email).first()
        if user:
            return render_template('accounts/register.html',
                                   msg='Email already registered',
                                   success=False,
                                   form=create_account_form)

        # else we can create the user
        user = Users(**request.form)
        db.session.add(user)
        db.session.commit()

        return render_template('accounts/register.html',
                               msg='User created please <a href="/login">login</a>',
                               success=True,
                               form=create_account_form)

    else:
        return render_template('accounts/register.html', form=create_account_form)



@blueprint.route('/password')
def password():
    return render_template('accounts/password.html')

from flask_login import login_required
from flask import request, redirect, url_for, render_template, flash

@blueprint.route('/profil', methods=['GET', 'POST'])
@login_required
def profil():
    if request.method == 'POST':
        # Mise à jour des informations de l'utilisateur
        current_user.username = request.form['username']
        current_user.email = request.form['email']
        
        # Gestion du mot de passe si l'utilisateur souhaite le changer
        password = request.form['password']
        if password:  # Si le mot de passe est renseigné
            current_user.password = hash_pass(password)  # Hachage du nouveau mot de passe

        db.session.commit()
        return redirect(url_for('authentication_blueprint.profil'))  # Redirection après la mise à jour

    # Affichage du profil de l'utilisateur
    return render_template('accounts/profil.html', user=current_user)



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
