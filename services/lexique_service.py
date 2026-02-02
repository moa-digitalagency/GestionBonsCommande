from models import db
from models.lexique import LexiqueEntry, LexiqueSuggestion
from flask_login import current_user

class LexiqueService:
    @staticmethod
    def search(term, lang=None):
        if not term:
            return None, 0.0
        
        term_lower = term.lower().strip()
        
        entries = LexiqueEntry.query.filter_by(is_validated=True).all()
        
        for entry in entries:
            if entry.matches(term_lower):
                entry.increment_usage()
                db.session.commit()
                return entry, 1.0
        
        for entry in entries:
            translations = entry.translations or {}
            for t_lang, translation in translations.items():
                if translation and term_lower in translation.lower():
                    entry.increment_usage()
                    db.session.commit()
                    return entry, 0.8
            
            for alias in (entry.aliases or []):
                if term_lower in alias.lower():
                    entry.increment_usage()
                    db.session.commit()
                    return entry, 0.7
        
        return None, 0.0
    
    @staticmethod
    def translate(term, from_lang=None, to_lang='fr'):
        entry, score = LexiqueService.search(term)
        
        if entry:
            translation = entry.get_translation(to_lang)
            return {
                'original': term,
                'translation': translation,
                'confidence': score,
                'source': 'dictionary',
                'entry_id': entry.id
            }
        
        return {
            'original': term,
            'translation': term,
            'confidence': 0.0,
            'source': 'unknown',
            'entry_id': None
        }
    
    @staticmethod
    def get_all_entries(category=None):
        query = LexiqueEntry.query.filter_by(is_validated=True)
        if category:
            query = query.filter_by(category=category)
        return query.order_by(LexiqueEntry.usage_count.desc()).all()
    
    @staticmethod
    def suggest_term(original_term, suggested_translations, category=None, context=None, source_language=None):
        suggestion = LexiqueSuggestion(
            suggested_by_id=current_user.id,
            company_id=current_user.company_id,
            original_term=original_term,
            source_language=source_language,
            suggested_translations=suggested_translations,
            category=category,
            context=context,
            status='pending'
        )
        
        db.session.add(suggestion)
        db.session.commit()
        
        return suggestion
    
    @staticmethod
    def get_pending_suggestions():
        return LexiqueSuggestion.query.filter_by(status='pending').order_by(
            LexiqueSuggestion.created_at.desc()
        ).all()
    
    @staticmethod
    def approve_suggestion(suggestion_id, translations=None, category=None):
        suggestion = LexiqueSuggestion.query.get(suggestion_id)
        if not suggestion:
            raise ValueError("Suggestion non trouvée")
        
        final_translations = translations or suggestion.suggested_translations
        final_category = category or suggestion.category or 'general'
        
        entry = LexiqueEntry(
            category=final_category,
            translations=final_translations,
            aliases=[suggestion.original_term],
            is_validated=True,
            usage_count=0
        )
        
        db.session.add(entry)
        
        suggestion.status = 'approved'
        suggestion.reviewed_by_id = current_user.id
        suggestion.lexique_entry_id = entry.id
        
        from datetime import datetime
        suggestion.reviewed_at = datetime.utcnow()
        
        db.session.commit()
        
        return entry
    
    @staticmethod
    def reject_suggestion(suggestion_id, notes=None):
        suggestion = LexiqueSuggestion.query.get(suggestion_id)
        if not suggestion:
            raise ValueError("Suggestion non trouvée")
        
        suggestion.status = 'rejected'
        suggestion.reviewed_by_id = current_user.id
        suggestion.review_notes = notes
        
        from datetime import datetime
        suggestion.reviewed_at = datetime.utcnow()
        
        db.session.commit()
        
        return suggestion
    
    @staticmethod
    def add_entry(translations, category='general', aliases=None):
        entry = LexiqueEntry(
            category=category,
            translations=translations,
            aliases=aliases or [],
            is_validated=True,
            usage_count=0
        )
        
        db.session.add(entry)
        db.session.commit()
        
        return entry
    
    @staticmethod
    def update_entry(entry_id, translations=None, category=None, aliases=None):
        entry = LexiqueEntry.query.get(entry_id)
        if not entry:
            raise ValueError("Entrée non trouvée")
        
        if translations is not None:
            entry.translations = translations
        if category is not None:
            entry.category = category
        if aliases is not None:
            entry.aliases = aliases
        
        db.session.commit()
        
        return entry
    
    @staticmethod
    def delete_entry(entry_id):
        entry = LexiqueEntry.query.get(entry_id)
        if not entry:
            raise ValueError("Entrée non trouvée")
        
        db.session.delete(entry)
        db.session.commit()
