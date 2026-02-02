from datetime import datetime
from models import db

class LexiqueEntry(db.Model):
    __tablename__ = 'lexique_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    
    category = db.Column(db.String(50), nullable=False, default='general')
    
    translations = db.Column(db.JSON, nullable=False, default=dict)
    
    aliases = db.Column(db.JSON, nullable=True)
    
    is_validated = db.Column(db.Boolean, default=True)
    usage_count = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_translation(self, lang='fr'):
        if self.translations and lang in self.translations:
            return self.translations[lang]
        if self.translations and 'fr' in self.translations:
            return self.translations['fr']
        return None
    
    def set_translation(self, lang, value):
        if not self.translations:
            self.translations = {}
        self.translations[lang] = value
    
    def add_alias(self, alias):
        if not self.aliases:
            self.aliases = []
        if alias.lower() not in [a.lower() for a in self.aliases]:
            self.aliases.append(alias)
    
    def matches(self, term):
        term_lower = term.lower().strip()
        for lang, translation in (self.translations or {}).items():
            if translation and translation.lower() == term_lower:
                return True
        for alias in (self.aliases or []):
            if alias.lower() == term_lower:
                return True
        return False
    
    def increment_usage(self):
        self.usage_count = (self.usage_count or 0) + 1
    
    def __repr__(self):
        fr_name = self.translations.get('fr', 'Unknown') if self.translations else 'Unknown'
        return f'<LexiqueEntry {fr_name}>'


class LexiqueSuggestion(db.Model):
    __tablename__ = 'lexique_suggestions'
    
    id = db.Column(db.Integer, primary_key=True)
    
    suggested_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=True)
    
    original_term = db.Column(db.String(200), nullable=False)
    source_language = db.Column(db.String(10), nullable=True)
    
    suggested_translations = db.Column(db.JSON, nullable=False, default=dict)
    
    category = db.Column(db.String(50), nullable=True)
    context = db.Column(db.Text, nullable=True)
    
    status = db.Column(db.String(20), nullable=False, default='pending')
    reviewed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    review_notes = db.Column(db.Text, nullable=True)
    
    lexique_entry_id = db.Column(db.Integer, db.ForeignKey('lexique_entries.id'), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    reviewed_by = db.relationship('User', foreign_keys=[reviewed_by_id])
    company = db.relationship('Company')
    lexique_entry = db.relationship('LexiqueEntry')
    
    def __repr__(self):
        return f'<LexiqueSuggestion {self.original_term}>'
