from models import db

class SiteSettings(db.Model):
    __tablename__ = 'site_settings'

    id = db.Column(db.Integer, primary_key=True)

    # Identité
    app_name = db.Column(db.String(100), default="BTP Premium")
    contact_email = db.Column(db.String(200))

    # Assets Visuels
    logo_url = db.Column(db.String(255))
    favicon_url = db.Column(db.String(255))
    primary_color = db.Column(db.String(20), default="#0f172a")

    # SEO Avancé
    meta_title_default = db.Column(db.String(60), default="BTP Premium - ERP BTP")
    meta_description_default = db.Column(db.String(160), default="Plateforme de gestion BTP")
    meta_keywords = db.Column(db.Text)
    og_image_url = db.Column(db.String(255))

    # Maintenance
    maintenance_mode = db.Column(db.Boolean, default=False)

    @staticmethod
    def get_instance():
        """Returns the singleton instance of SiteSettings, creating it if it doesn't exist."""
        settings = SiteSettings.query.first()
        if not settings:
            settings = SiteSettings()
            db.session.add(settings)
            db.session.commit()
        return settings
