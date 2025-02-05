from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, TextAreaField, FileField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional, Length, NumberRange
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, TextAreaField, FileField, SubmitField, SelectMultipleField
from wtforms.validators import DataRequired, Optional, Length, NumberRange
from flask_wtf.file import FileAllowed
from wtforms_sqlalchemy.fields import QuerySelectMultipleField
from apps.authentication.models import Ingredient

class IngredientForm(FlaskForm):
    # Champs de formulaire pour les ingrédients
    nom_commun = StringField('Nom Commun', validators=[DataRequired(message="Le nom commun est obligatoire"), Length(max=255)])
    nom_fon = StringField('Nom Fon', validators=[DataRequired(message="Le nom Fon est obligatoire"), Length(max=255)])
    nom_scientifique = StringField('Nom Scientifique', validators=[Optional(), Length(max=255)])
    partie = StringField('Partie Utilisée', validators=[Optional(), Length(max=255)])
    proprietes = TextAreaField('Propriétés', validators=[Optional()])
    latitude = FloatField('Latitude', validators=[Optional(), NumberRange(min=-90, max=90, message="La latitude doit être comprise entre -90 et 90")])
    longitude = FloatField('Longitude', validators=[Optional(), NumberRange(min=-180, max=180, message="La longitude doit être comprise entre -180 et 180")])
    images = FileField('Image (Chemin ou URL)', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg'], 'Seules les images au format JPG, PNG ou JPEG sont autorisées')])
    like = IntegerField('Nombre de Likes', validators=[Optional()])
    user_id = IntegerField('ID Utilisateur', validators=[Optional()])

    # Bouton de soumission
    submit = SubmitField('Enregistrer')


class RemedeForm(FlaskForm):
    # Champs de formulaire pour les remèdes
    nom = StringField('Nom du Remède', validators=[DataRequired(message="Le nom du remède est obligatoire")])
    description = TextAreaField('Description', validators=[Optional()])
    preparation = TextAreaField('Préparation', validators=[Optional()])
    latitude = FloatField('Latitude', validators=[Optional(), NumberRange(min=-90, max=90, message="La latitude doit être comprise entre -90 et 90")])
    longitude = FloatField('Longitude', validators=[Optional(), NumberRange(min=-180, max=180, message="La longitude doit être comprise entre -180 et 180")])
    indications = TextAreaField('Indications', validators=[Optional()])
    dosage = TextAreaField('Dosage', validators=[Optional()])
    precautions = TextAreaField('Précautions', validators=[Optional()])
    images = FileField('Image', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg'], 'Seules les images au format JPG, PNG ou JPEG sont autorisées')])
    video = FileField('Vidéo', validators=[Optional(), FileAllowed(['mp4', 'avi'], 'Seules les vidéos au format MP4 ou AVI sont autorisées')])
    liens = StringField('Liens Utiles', validators=[Optional()])

    # Bouton de soumission
    submit = SubmitField('Enregistrer')

    def __init__(self, remede=None, *args, **kwargs):
        super(RemedeForm, self).__init__(*args, **kwargs)
        if remede:
            self.nom.data = remede.nom
            self.description.data = remede.description
            self.preparation.data = remede.preparation
            self.latitude.data = remede.latitude
            self.longitude.data = remede.longitude
            self.indications.data = remede.indications
            self.dosage.data = remede.dosage
            self.precautions.data = remede.precautions
            self.liens.data = remede.liens


class MaladieForm(FlaskForm):
    nom_commun = StringField(
        'Nom Commun', 
        validators=[DataRequired(), Length(max=255)]
    )
    nom_fon = StringField(
        'Nom en Fon', 
        validators=[DataRequired(), Length(max=255)]
    )
    proprietes = TextAreaField(
        'Propriétés'
    )
    images = FileField(
        'Image', 
        validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images uniquement!')]
    )
    submit = SubmitField('Enregistrer')



from wtforms import StringField, TextAreaField, DateField, SubmitField, SelectMultipleField
from wtforms.validators import URL

class ArticleForm(FlaskForm):
    titre = StringField(
        'Titre',
        validators=[DataRequired(), Length(max=255)]
    )
    auteur = StringField(
        'Auteur',
        validators=[Length(max=255)]
    )
    resume = TextAreaField(
        'Résumé'
    )
    date_publication = DateField(
        'Date de Publication',
        format='%Y-%m-%d'
    )
    lien = StringField(
        'Lien',
        validators=[Length(max=255), URL(require_tld=True, message="Lien invalide")]
    )
    remedes = SelectMultipleField(
        'Remèdes Associés',
        coerce=int  # Les IDs des remèdes
    )
    ingredients = SelectMultipleField(
        'Ingrédients Associés',
        coerce=int  # Les IDs des ingrédients
    )
    submit = SubmitField('Enregistrer')


