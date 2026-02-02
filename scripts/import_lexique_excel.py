#!/usr/bin/env python
"""Import lexique data from Excel file"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import openpyxl
from app import create_app, db
from models.lexique import LexiqueEntry

def import_lexique(filepath):
    """Import lexique entries from Excel file"""
    app = create_app()
    
    with app.app_context():
        wb = openpyxl.load_workbook(filepath)
        sheet = wb.active
        
        imported = 0
        updated = 0
        
        for row in sheet.iter_rows(min_row=2, values_only=True):
            francais, darija_arabe, darija_latin = row
            
            if not francais:
                continue
            
            francais = francais.strip()
            
            existing = LexiqueEntry.query.filter(
                LexiqueEntry.translations['fr'].astext == francais
            ).first()
            
            translations = {
                'fr': francais,
                'ar': darija_arabe.strip() if darija_arabe else '',
                'darija': darija_latin.strip() if darija_latin else '',
                'en': '',
                'es': ''
            }
            
            if existing:
                existing.translations = translations
                updated += 1
            else:
                entry = LexiqueEntry(
                    category='materiau',
                    translations=translations,
                    is_validated=True
                )
                db.session.add(entry)
                imported += 1
        
        db.session.commit()
        print(f"Import terminé: {imported} nouveaux termes, {updated} mis à jour")

if __name__ == '__main__':
    filepath = 'attached_assets/lexique_batiment_darija_1000_(1)_1770058330425.xlsx'
    import_lexique(filepath)
