# /* * Nom de l'application : BTP Commande
#  * Description : Paramètres globaux du site
#  * Produit de : MOA Digital Agency, www.myoneart.com
#  * Fait par : Aisance KALONJI, www.aisancekalonji.com
#  * Auditer par : La CyberConfiance, www.cyberconfiance.com
#  */

import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db
from models.settings import SiteSettings

settings_bp = Blueprint('settings', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'ico', 'svg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@settings_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    # Only Admin/Super Admin should access settings
    if not current_user.is_admin():
        flash("Vous n'avez pas la permission d'accéder à cette page.", "danger")
        return redirect(url_for('main.dashboard'))

    settings = SiteSettings.get_instance()

    if request.method == 'POST':
        try:
            # Identity
            settings.app_name = request.form.get('app_name')
            settings.contact_email = request.form.get('contact_email')
            settings.primary_color = request.form.get('primary_color')

            # SEO
            settings.meta_title_default = request.form.get('meta_title_default')
            settings.meta_description_default = request.form.get('meta_description_default')
            settings.meta_keywords = request.form.get('meta_keywords')

            # System
            settings.maintenance_mode = 'maintenance_mode' in request.form

            # Handle File Uploads
            upload_folder = os.path.join(current_app.static_folder, 'uploads')
            os.makedirs(upload_folder, exist_ok=True)

            # Logo
            if 'logo' in request.files:
                file = request.files['logo']
                if file and file.filename != '' and allowed_file(file.filename):
                    ext = file.filename.rsplit('.', 1)[1].lower()
                    filename = f"site_logo.{ext}"
                    filepath = os.path.join(upload_folder, filename)
                    file.save(filepath)
                    settings.logo_url = f"uploads/{filename}"

            # Favicon
            if 'favicon' in request.files:
                file = request.files['favicon']
                if file and file.filename != '' and allowed_file(file.filename):
                    ext = file.filename.rsplit('.', 1)[1].lower()
                    filename = f"site_favicon.{ext}"
                    filepath = os.path.join(upload_folder, filename)
                    file.save(filepath)
                    settings.favicon_url = f"uploads/{filename}"

            # OG Image
            if 'og_image' in request.files:
                file = request.files['og_image']
                if file and file.filename != '' and allowed_file(file.filename):
                    ext = file.filename.rsplit('.', 1)[1].lower()
                    filename = f"site_og_image.{ext}"
                    filepath = os.path.join(upload_folder, filename)
                    file.save(filepath)
                    settings.og_image_url = f"uploads/{filename}"

            db.session.commit()
            flash('Paramètres mis à jour avec succès.', 'success')
            return redirect(url_for('settings.index'))

        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la mise à jour: {str(e)}', 'danger')

    return render_template('settings.html', settings=settings)
