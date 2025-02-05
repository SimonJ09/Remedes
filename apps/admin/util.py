# -*- encoding: utf-8 -*-
import os
import hashlib
import binascii
from apps.config import Config

import os
from werkzeug.utils import secure_filename
from flask import current_app

def save_file(file, subfolder="ingredients"):
    # Générer le chemin du sous-dossier
    upload_folder = os.path.join(Config.UPLOAD_FOLDER, subfolder)
    # Créer le sous-dossier s'il n'existe pas
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    # Générer le chemin complet du fichier
    file_path = os.path.join(upload_folder, file.filename)
    file_path = file_path.replace('\\', '/')
    # Sauvegarder le fichier
    file.save(file_path)
    # Retourner le chemin relatif pour l'utilisation dans la base de données ou ailleurs
    return os.path.join(subfolder, file.filename)


