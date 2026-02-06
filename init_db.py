#!/usr/bin/env python3
import os
import sys
from sqlalchemy import inspect, text
from sqlalchemy.exc import OperationalError

# /* * Nom de l'application : BTP Commande
#  * Description : Script d'initialisation de la base de données
#  * Produit de : MOA Digital Agency, www.myoneart.com
#  * Fait par : Aisance KALONJI, www.aisancekalonji.com
#  * Auditer par : La CyberConfiance, www.cyberconfiance.com
#  */

# Ensure we are running in the correct environment
if os.path.exists('venv') and sys.prefix == sys.base_prefix:
    print("WARNING: You seem to be running outside the virtual environment.")
    print("Please activate it first: source venv/bin/activate")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db
from models.company import Company
from models.user import User
from models.lexique import LexiqueEntry
from models.settings import SiteSettings

def init_database():
    print("Starting database initialization...")
    app = create_app()
    
    with app.app_context():
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()

        tables_created = 0
        tables_checked = 0

        # Iterate over all models defined in SQLAlchemy metadata
        for table_name, table in db.metadata.tables.items():
            if table_name not in existing_tables:
                print(f"Creating table: {table_name}")
                table.create(db.engine)
                tables_created += 1
            else:
                print(f"Checking schema for table: {table_name}")
                tables_checked += 1
                existing_columns = [c['name'] for c in inspector.get_columns(table_name)]

                for column in table.columns:
                    if column.name not in existing_columns:
                        print(f"Adding missing column: {column.name} to {table_name}")
                        col_type = column.type.compile(db.engine.dialect)

                        # SQLite ALTER TABLE ADD COLUMN limitation:
                        # Cannot add NOT NULL column without DEFAULT value.
                        # We append DEFAULT NULL if it's nullable, or we rely on the DB engine to handle it if provided.
                        # For this script, we assume the column definition is compatible or we catch the error.

                        try:
                            with db.engine.connect() as conn:
                                sql = f'ALTER TABLE "{table_name}" ADD COLUMN "{column.name}" {col_type}'
                                conn.execute(text(sql))
                                conn.commit()
                                print(f"Successfully added column {column.name}")
                        except OperationalError as e:
                            print(f"Operational Error adding column {column.name}: {e}")
                            if "duplicate column name" in str(e).lower():
                                print("Column already exists (race condition?), skipping.")
                            else:
                                print("CRITICAL: Could not add column. Manual intervention may be required.")
                        except Exception as e:
                            print(f"Error adding column {column.name} to {table_name}: {e}")

        print(f"Schema verification complete! (Tables created: {tables_created}, Checked: {tables_checked})")
        
        # Initialize Site Settings
        try:
            settings = SiteSettings.get_instance()
            print(f"Site settings initialized: {settings.app_name}")
        except Exception as e:
            print(f"Error initializing site settings: {e}")

        # Create or Update Super Admin
        try:
            admin_email = app.config.get('SUPER_ADMIN_EMAIL')
            admin_password = app.config.get('SUPER_ADMIN_PASSWORD')

            if admin_email and admin_password:
                admin = User.query.filter_by(email=admin_email).first()

                if not admin:
                    admin = User(
                        email=admin_email,
                        first_name=app.config.get('SUPER_ADMIN_FIRST_NAME', 'Super'),
                        last_name=app.config.get('SUPER_ADMIN_LAST_NAME', 'Admin'),
                        role='super_admin',
                        preferred_language='fr',
                        is_active=True
                    )
                    admin.set_password(admin_password)
                    db.session.add(admin)
                    print(f"Super Admin created: {admin_email}")
                else:
                    # Update admin details if config changed
                    admin.first_name = app.config.get('SUPER_ADMIN_FIRST_NAME', admin.first_name)
                    admin.last_name = app.config.get('SUPER_ADMIN_LAST_NAME', admin.last_name)
                    # Only reset password if you want to enforce config password on every deploy
                    # admin.set_password(admin_password)
                    print(f"Super Admin exists: {admin_email}")

                db.session.commit()
            else:
                print("Skipping Super Admin creation: Credentials not found in config.")
        except Exception as e:
            print(f"Error managing Super Admin: {e}")
            db.session.rollback()
        
        # Populate Dictionary
        try:
            if LexiqueEntry.query.count() == 0:
                populate_btp_dictionary()
                print("BTP Dictionary populated with initial terms!")
            else:
                print("Dictionary already populated.")
        except Exception as e:
            print(f"Error checking/populating dictionary: {e}")

        print("Database initialization complete!")

def populate_btp_dictionary():
    btp_terms = [
        {
            "category": "materiau",
            "translations": {"fr": "Ciment", "ar": "إسمنت", "darija_lat": "Sima", "en": "Cement", "es": "Cemento"},
            "aliases": ["siment", "ciment portland", "cma"]
        },
        {
            "category": "materiau",
            "translations": {"fr": "Sable", "ar": "رمل", "darija_lat": "Rmel", "en": "Sand", "es": "Arena"},
            "aliases": ["sabla", "sable de mer", "sable de carrière"]
        },
        {
            "category": "materiau",
            "translations": {"fr": "Gravette", "ar": "حصى", "darija_lat": "Bghli", "en": "Gravel", "es": "Grava"},
            "aliases": ["gravier", "gravillon", "bghli 15/25", "bghli 5/15"]
        },
        {
            "category": "materiau",
            "translations": {"fr": "Fer à béton", "ar": "حديد التسليح", "darija_lat": "Hdid", "en": "Rebar", "es": "Varilla de hierro"},
            "aliases": ["acier", "fer", "hdid lbeton", "armature"]
        },
        {
            "category": "materiau",
            "translations": {"fr": "Briques", "ar": "طوب", "darija_lat": "Brik", "en": "Bricks", "es": "Ladrillos"},
            "aliases": ["brique rouge", "brique creuse", "toub", "6 trous", "8 trous", "12 trous"]
        },
        {
            "category": "materiau",
            "translations": {"fr": "Parpaing", "ar": "بلوك إسمنتي", "darija_lat": "Hourdis", "en": "Concrete block", "es": "Bloque de hormigón"},
            "aliases": ["bloc", "agglo", "bloc beton", "parpen"]
        },
        {
            "category": "materiau",
            "translations": {"fr": "Eau", "ar": "ماء", "darija_lat": "Lma", "en": "Water", "es": "Agua"},
            "aliases": ["eau de gâchage", "ma"]
        },
        {
            "category": "materiau",
            "translations": {"fr": "Béton", "ar": "خرسانة", "darija_lat": "Beton", "en": "Concrete", "es": "Hormigón"},
            "aliases": ["beton arme", "beton pret", "BPE"]
        },
        {
            "category": "materiau",
            "translations": {"fr": "Mortier", "ar": "ملاط", "darija_lat": "Mortier", "en": "Mortar", "es": "Mortero"},
            "aliases": ["mortier colle", "mortier de pose"]
        },
        {
            "category": "materiau",
            "translations": {"fr": "Plâtre", "ar": "جبس", "darija_lat": "Jbs", "en": "Plaster", "es": "Yeso"},
            "aliases": ["platre", "jibs", "gips"]
        },
        {
            "category": "materiau",
            "translations": {"fr": "Carrelage", "ar": "بلاط", "darija_lat": "Zlij", "en": "Tiles", "es": "Azulejos"},
            "aliases": ["zellige", "zelij", "faience", "carreau"]
        },
        {
            "category": "materiau",
            "translations": {"fr": "Bois", "ar": "خشب", "darija_lat": "Lkhcheb", "en": "Wood", "es": "Madera"},
            "aliases": ["khcheb", "bois rouge", "madrier", "chevron"]
        },
        {
            "category": "materiau",
            "translations": {"fr": "Peinture", "ar": "دهان", "darija_lat": "Sbagha", "en": "Paint", "es": "Pintura"},
            "aliases": ["sbgha", "dhan", "peinture acrylique", "peinture vinylique"]
        },
        {
            "category": "materiau",
            "translations": {"fr": "Enduit", "ar": "طلاء", "darija_lat": "Tla", "en": "Coating", "es": "Enlucido"},
            "aliases": ["enduit de facade", "crepi", "tla lhit"]
        },
        {
            "category": "materiau",
            "translations": {"fr": "Chaux", "ar": "جير", "darija_lat": "Jir", "en": "Lime", "es": "Cal"},
            "aliases": ["chaux hydraulique", "chaux vive"]
        },
        {
            "category": "materiau",
            "translations": {"fr": "Étanchéité", "ar": "عزل مائي", "darija_lat": "Etancheite", "en": "Waterproofing", "es": "Impermeabilización"},
            "aliases": ["membrane", "bitume", "roofing"]
        },
        {
            "category": "materiau",
            "translations": {"fr": "Isolation", "ar": "عزل حراري", "darija_lat": "Isolation", "en": "Insulation", "es": "Aislamiento"},
            "aliases": ["polystyrene", "laine de verre", "isolant"]
        },
        {
            "category": "materiau",
            "translations": {"fr": "PVC", "ar": "بي في سي", "darija_lat": "PVC", "en": "PVC", "es": "PVC"},
            "aliases": ["tube pvc", "tuyau pvc", "pvc rigide"]
        },
        {
            "category": "materiau",
            "translations": {"fr": "Fil de fer", "ar": "سلك حديد", "darija_lat": "Fil", "en": "Wire", "es": "Alambre"},
            "aliases": ["fil recuit", "fil de ligature", "slk"]
        },
        {
            "category": "materiau",
            "translations": {"fr": "Clous", "ar": "مسامير", "darija_lat": "Msamer", "en": "Nails", "es": "Clavos"},
            "aliases": ["clou", "masmar", "pointe"]
        },
        {
            "category": "materiau",
            "translations": {"fr": "Vis", "ar": "براغي", "darija_lat": "Vis", "en": "Screws", "es": "Tornillos"},
            "aliases": ["visse", "boulon"]
        },
        {
            "category": "materiau",
            "translations": {"fr": "Tôle", "ar": "صفيحة", "darija_lat": "Tol", "en": "Sheet metal", "es": "Chapa"},
            "aliases": ["tole ondulee", "tole galvanisee", "sfih"]
        },
        {
            "category": "materiau",
            "translations": {"fr": "Tube acier", "ar": "أنبوب فولاذي", "darija_lat": "Tube", "en": "Steel tube", "es": "Tubo de acero"},
            "aliases": ["tube carre", "tube rond", "profilé"]
        },
        {
            "category": "materiau",
            "translations": {"fr": "Aluminium", "ar": "ألومنيوم", "darija_lat": "Aluminium", "en": "Aluminum", "es": "Aluminio"},
            "aliases": ["alu", "profile alu", "menuiserie alu"]
        },
        {
            "category": "materiau",
            "translations": {"fr": "Verre", "ar": "زجاج", "darija_lat": "Zjaj", "en": "Glass", "es": "Vidrio"},
            "aliases": ["vitre", "double vitrage", "zaj"]
        },
        {
            "category": "materiau",
            "translations": {"fr": "Câble électrique", "ar": "كابل كهربائي", "darija_lat": "Kabel", "en": "Electric cable", "es": "Cable eléctrico"},
            "aliases": ["fil electrique", "cable", "gaine"]
        },
        {
            "category": "materiau",
            "translations": {"fr": "Interrupteur", "ar": "مفتاح كهربائي", "darija_lat": "Interrupteur", "en": "Switch", "es": "Interruptor"},
            "aliases": ["inter", "bouton"]
        },
        {
            "category": "materiau",
            "translations": {"fr": "Prise électrique", "ar": "مقبس كهربائي", "darija_lat": "Prise", "en": "Electrical outlet", "es": "Enchufe"},
            "aliases": ["prise de courant", "prise murale"]
        },
        {
            "category": "materiau",
            "translations": {"fr": "Tuyau PPR", "ar": "أنبوب PPR", "darija_lat": "PPR", "en": "PPR pipe", "es": "Tubo PPR"},
            "aliases": ["ppr", "tube ppr", "plomberie"]
        },
        {
            "category": "materiau",
            "translations": {"fr": "Robinet", "ar": "صنبور", "darija_lat": "Robine", "en": "Faucet", "es": "Grifo"},
            "aliases": ["robinetterie", "mitigeur", "snbor"]
        },
        {
            "category": "materiel",
            "translations": {"fr": "Bétonnière", "ar": "خلاطة إسمنت", "darija_lat": "Betonniere", "en": "Concrete mixer", "es": "Hormigonera"},
            "aliases": ["betoniere", "malaxeur", "khallata"]
        },
        {
            "category": "materiel",
            "translations": {"fr": "Brouette", "ar": "عربة يد", "darija_lat": "Brouet", "en": "Wheelbarrow", "es": "Carretilla"},
            "aliases": ["brouetta", "charette"]
        },
        {
            "category": "materiel",
            "translations": {"fr": "Pelle", "ar": "مجرفة", "darija_lat": "Pala", "en": "Shovel", "es": "Pala"},
            "aliases": ["pala", "mjrfa"]
        },
        {
            "category": "materiel",
            "translations": {"fr": "Pioche", "ar": "معول", "darija_lat": "Fass", "en": "Pickaxe", "es": "Pico"},
            "aliases": ["fas", "maol"]
        },
        {
            "category": "materiel",
            "translations": {"fr": "Truelle", "ar": "مالج", "darija_lat": "Truelle", "en": "Trowel", "es": "Paleta"},
            "aliases": ["malj", "taloche"]
        },
        {
            "category": "materiel",
            "translations": {"fr": "Niveau", "ar": "ميزان", "darija_lat": "Niveau", "en": "Level", "es": "Nivel"},
            "aliases": ["niveau a bulle", "mizan"]
        },
        {
            "category": "materiel",
            "translations": {"fr": "Mètre", "ar": "شريط قياس", "darija_lat": "Mtr", "en": "Tape measure", "es": "Cinta métrica"},
            "aliases": ["metre ruban", "decametre", "mtr"]
        },
        {
            "category": "materiel",
            "translations": {"fr": "Échafaudage", "ar": "سقالة", "darija_lat": "Echafaudage", "en": "Scaffolding", "es": "Andamio"},
            "aliases": ["skala", "plateforme"]
        },
        {
            "category": "materiel",
            "translations": {"fr": "Échelle", "ar": "سلم", "darija_lat": "Sellom", "en": "Ladder", "es": "Escalera"},
            "aliases": ["echele", "escabeau", "slm"]
        },
        {
            "category": "materiel",
            "translations": {"fr": "Perceuse", "ar": "مثقاب", "darija_lat": "Perceuse", "en": "Drill", "es": "Taladro"},
            "aliases": ["perforateur", "visseuse", "drill"]
        },
        {
            "category": "materiel",
            "translations": {"fr": "Disqueuse", "ar": "قاطعة دائرية", "darija_lat": "Disqueuse", "en": "Angle grinder", "es": "Amoladora"},
            "aliases": ["meuleuse", "flex"]
        },
        {
            "category": "materiel",
            "translations": {"fr": "Scie", "ar": "منشار", "darija_lat": "Scie", "en": "Saw", "es": "Sierra"},
            "aliases": ["scie circulaire", "scie sauteuse", "mnshar"]
        },
        {
            "category": "materiel",
            "translations": {"fr": "Marteau", "ar": "مطرقة", "darija_lat": "Martou", "en": "Hammer", "es": "Martillo"},
            "aliases": ["matrka", "masse"]
        },
        {
            "category": "materiel",
            "translations": {"fr": "Coffrage", "ar": "قوالب", "darija_lat": "Coffrage", "en": "Formwork", "es": "Encofrado"},
            "aliases": ["banche", "panneaux", "qwalib"]
        },
        {
            "category": "materiel",
            "translations": {"fr": "Vibreur", "ar": "هزاز", "darija_lat": "Vibreur", "en": "Vibrator", "es": "Vibrador"},
            "aliases": ["aiguille vibrante", "pervibrator"]
        },
        {
            "category": "materiel",
            "translations": {"fr": "Pompe à béton", "ar": "مضخة خرسانة", "darija_lat": "Pompe", "en": "Concrete pump", "es": "Bomba de hormigón"},
            "aliases": ["pompe", "pompage"]
        },
        {
            "category": "materiel",
            "translations": {"fr": "Grue", "ar": "رافعة", "darija_lat": "Grue", "en": "Crane", "es": "Grúa"},
            "aliases": ["gru", "grua"]
        },
        {
            "category": "materiel",
            "translations": {"fr": "Casque", "ar": "خوذة", "darija_lat": "Casque", "en": "Helmet", "es": "Casco"},
            "aliases": ["casque de chantier", "khoda"]
        },
        {
            "category": "materiel",
            "translations": {"fr": "Gants", "ar": "قفازات", "darija_lat": "Gants", "en": "Gloves", "es": "Guantes"},
            "aliases": ["gant de travail", "qffazat"]
        },
        {
            "category": "materiel",
            "translations": {"fr": "Chaussures de sécurité", "ar": "أحذية أمان", "darija_lat": "Sbat", "en": "Safety shoes", "es": "Zapatos de seguridad"},
            "aliases": ["chaussures", "brodequins", "sbat securite"]
        }
    ]
    
    for term_data in btp_terms:
        entry = LexiqueEntry(
            category=term_data["category"],
            translations=term_data["translations"],
            aliases=term_data.get("aliases", []),
            is_validated=True,
            usage_count=0
        )
        db.session.add(entry)
    
    db.session.commit()

if __name__ == '__main__':
    init_database()
