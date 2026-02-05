import sys
import os
import openpyxl
from sqlalchemy.orm.attributes import flag_modified

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db
from models.lexique import LexiqueEntry

def import_lexique(file_path):
    app = create_app()
    with app.app_context():
        print(f"Loading workbook from {file_path}")
        try:
            wb = openpyxl.load_workbook(file_path)
            sheet = wb.active
        except Exception as e:
            print(f"Error loading Excel file: {e}")
            return

        # Headers: ['Francais', 'Darija_arabe', 'Darija_latin']
        # Map headers to language codes
        header_map = {
            'Francais': 'fr',
            'Darija_arabe': 'ar',
            'Darija_latin': 'dr'
        }

        # Identify column indices
        headers = [cell.value for cell in sheet[1]]
        col_indices = {}
        for idx, header in enumerate(headers):
            if header in header_map:
                col_indices[header_map[header]] = idx

        print(f"Column mapping: {col_indices}")

        count = 0
        updated = 0

        # Pre-load existing entries to avoid N queries
        print("Loading existing entries...")
        all_entries = LexiqueEntry.query.all()
        entry_map = {}
        for e in all_entries:
            fr = e.get_translation('fr')
            if fr:
                entry_map[fr.lower()] = e

        print(f"Found {len(entry_map)} existing entries.")

        for row_idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True)):
            translations = {}
            for lang, idx in col_indices.items():
                if idx < len(row) and row[idx]:
                    translations[lang] = str(row[idx]).strip()

            if 'fr' not in translations:
                continue

            french_term = translations['fr']

            entry = entry_map.get(french_term.lower())

            if entry:
                # Update
                current_translations = entry.translations.copy() # Copy to avoid mutation issues
                current_translations.update(translations)
                entry.translations = current_translations
                # flag_modified(entry, "translations") # Usually needed if modifying in place, but reassignment handles it too? Better safe.
                flag_modified(entry, "translations")
                updated += 1
            else:
                # Create
                entry = LexiqueEntry(
                    category='general', # Default category
                    translations=translations,
                    aliases=[],
                    is_validated=True
                )
                db.session.add(entry)
                entry_map[french_term.lower()] = entry
                count += 1

            if (count + updated) % 100 == 0:
                print(f"Processed {count + updated} items...")

        db.session.commit()
        print(f"Import complete. Created {count} entries, Updated {updated} entries.")

if __name__ == '__main__':
    file_path = 'attached_assets/lexique_batiment_darija_1000_(1)_1770058330425.xlsx'
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
    else:
        import_lexique(file_path)
