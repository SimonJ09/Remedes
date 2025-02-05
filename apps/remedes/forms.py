# -*- encoding: utf-8 -*-


from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import Email, DataRequired

from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length

from apps.authentication.models import Users
from apps.authentication.models import Ingredient
from apps.authentication.models import Remede
from apps.authentication.models import RemedeIngredient


class CommentaireForm(FlaskForm):
    like = IntegerField(
        'Like',
        default=0
    )
    comment = StringField(
        'Commentaire',
        validators=[
            DataRequired(message="Le commentaire ne peut pas être vide."),
            Length(max=255, message="Le commentaire ne peut pas dépasser 255 caractères.")
        ]
    )
    submit = SubmitField('Soumettre')
