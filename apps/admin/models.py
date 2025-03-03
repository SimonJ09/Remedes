# -*- encoding: utf-8 -*-
from flask_login import UserMixin
from apps.authentication.util import is_user_admin
from apps import db, login_manager
from flask import render_template, redirect, request, url_for
from flask_login import (
    current_user,
    login_user,
    logout_user
)





