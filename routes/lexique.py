from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_required
from models import db
from models.lexique import LexiqueEntry, LexiqueSuggestion
from security.decorators import super_admin_required, tenant_required
from services.lexique_service import LexiqueService
from services.i18n_service import i18n
from config.settings import Config

lexique_bp = Blueprint('lexique', __name__)

@lexique_bp.route('/')
@login_required
def index():
    category = request.args.get('category', '')
    search = request.args.get('search', '').strip()
    
    entries = LexiqueEntry.query.filter_by(is_validated=True)
    
    if category:
        entries = entries.filter_by(category=category)
    
    if search:
        entries = entries.all()
        filtered = []
        for entry in entries:
            if entry.matches(search):
                filtered.append(entry)
                continue
            for lang, trans in (entry.translations or {}).items():
                if trans and search.lower() in trans.lower():
                    filtered.append(entry)
                    break
        entries = filtered
    else:
        entries = entries.order_by(LexiqueEntry.usage_count.desc()).all()
    
    return render_template('lexique/index.html', entries=entries, 
                         current_category=category, search=search,
                         languages=Config.SUPPORTED_LANGUAGES)

@lexique_bp.route('/search')
@login_required
def search():
    query = request.args.get('q', '').strip()
    lang = request.args.get('lang', 'fr')
    
    if not query or len(query) < 2:
        return jsonify([])
    
    entry, score = LexiqueService.search(query)
    
    if entry:
        return jsonify({
            'found': True,
            'translation': entry.get_translation(lang),
            'translations': entry.translations,
            'confidence': score,
            'category': entry.category
        })
    
    return jsonify({'found': False, 'confidence': 0})

@lexique_bp.route('/suggest', methods=['GET', 'POST'])
@login_required
@tenant_required
def suggest():
    if request.method == 'POST':
        original_term = request.form.get('original_term', '').strip()
        source_language = request.form.get('source_language', '')
        category = request.form.get('category', 'general')
        context = request.form.get('context', '').strip()
        
        translations = {}
        for lang in Config.SUPPORTED_LANGUAGES:
            trans = request.form.get(f'translation_{lang}', '').strip()
            if trans:
                translations[lang] = trans
        
        if not original_term:
            flash(i18n.translate('Le terme original est obligatoire.'), 'danger')
            return render_template('lexique/suggest.html', languages=Config.SUPPORTED_LANGUAGES)
        
        if not translations:
            flash(i18n.translate('Veuillez fournir au moins une traduction.'), 'danger')
            return render_template('lexique/suggest.html', languages=Config.SUPPORTED_LANGUAGES)
        
        try:
            suggestion = LexiqueService.suggest_term(
                original_term=original_term,
                suggested_translations=translations,
                category=category,
                context=context,
                source_language=source_language
            )
            flash(i18n.translate('Votre suggestion a été soumise. Elle sera examinée par un administrateur.'), 'success')
            return redirect(url_for('lexique.index'))
        except Exception as e:
            flash(i18n.translate('Erreur: {}').format(str(e)), 'danger')
    
    return render_template('lexique/suggest.html', languages=Config.SUPPORTED_LANGUAGES)

@lexique_bp.route('/admin')
@login_required
@super_admin_required
def admin():
    pending = LexiqueSuggestion.query.filter_by(status='pending').order_by(
        LexiqueSuggestion.created_at.desc()
    ).all()
    
    recent = LexiqueSuggestion.query.filter(
        LexiqueSuggestion.status.in_(['approved', 'rejected'])
    ).order_by(LexiqueSuggestion.reviewed_at.desc()).limit(20).all()
    
    return render_template('lexique/admin.html', pending=pending, recent=recent,
                         languages=Config.SUPPORTED_LANGUAGES)

@lexique_bp.route('/admin/suggestion/<int:suggestion_id>/approve', methods=['POST'])
@login_required
@super_admin_required
def approve_suggestion(suggestion_id):
    translations = {}
    for lang in Config.SUPPORTED_LANGUAGES:
        trans = request.form.get(f'translation_{lang}', '').strip()
        if trans:
            translations[lang] = trans
    
    category = request.form.get('category', 'general')
    
    try:
        LexiqueService.approve_suggestion(suggestion_id, translations or None, category)
        flash(i18n.translate('Suggestion approuvée et ajoutée au dictionnaire.'), 'success')
    except Exception as e:
        flash(i18n.translate('Erreur: {}').format(str(e)), 'danger')
    
    return redirect(url_for('lexique.admin'))

@lexique_bp.route('/admin/suggestion/<int:suggestion_id>/reject', methods=['POST'])
@login_required
@super_admin_required
def reject_suggestion(suggestion_id):
    notes = request.form.get('notes', '')
    
    try:
        LexiqueService.reject_suggestion(suggestion_id, notes)
        flash(i18n.translate('Suggestion rejetée.'), 'info')
    except Exception as e:
        flash(i18n.translate('Erreur: {}').format(str(e)), 'danger')
    
    return redirect(url_for('lexique.admin'))

@lexique_bp.route('/admin/entry/add', methods=['GET', 'POST'])
@login_required
@super_admin_required
def add_entry():
    if request.method == 'POST':
        category = request.form.get('category', 'general')
        aliases_str = request.form.get('aliases', '').strip()
        
        translations = {}
        for lang in Config.SUPPORTED_LANGUAGES:
            trans = request.form.get(f'translation_{lang}', '').strip()
            if trans:
                translations[lang] = trans
        
        if not translations.get('fr'):
            flash(i18n.translate('La traduction française est obligatoire.'), 'danger')
            return render_template('lexique/entry_form.html', entry=None, 
                                 languages=Config.SUPPORTED_LANGUAGES)
        
        aliases = [a.strip() for a in aliases_str.split(',') if a.strip()] if aliases_str else []
        
        try:
            LexiqueService.add_entry(translations, category, aliases)
            flash(i18n.translate('Entrée ajoutée au dictionnaire.'), 'success')
            return redirect(url_for('lexique.admin'))
        except Exception as e:
            flash(i18n.translate('Erreur: {}').format(str(e)), 'danger')
    
    return render_template('lexique/entry_form.html', entry=None, 
                         languages=Config.SUPPORTED_LANGUAGES)

@lexique_bp.route('/admin/entry/<int:entry_id>/edit', methods=['GET', 'POST'])
@login_required
@super_admin_required
def edit_entry(entry_id):
    entry = LexiqueEntry.query.get_or_404(entry_id)
    
    if request.method == 'POST':
        category = request.form.get('category', 'general')
        aliases_str = request.form.get('aliases', '').strip()
        
        translations = {}
        for lang in Config.SUPPORTED_LANGUAGES:
            trans = request.form.get(f'translation_{lang}', '').strip()
            if trans:
                translations[lang] = trans
        
        if not translations.get('fr'):
            flash(i18n.translate('La traduction française est obligatoire.'), 'danger')
            return render_template('lexique/entry_form.html', entry=entry, 
                                 languages=Config.SUPPORTED_LANGUAGES)
        
        aliases = [a.strip() for a in aliases_str.split(',') if a.strip()] if aliases_str else []
        
        try:
            LexiqueService.update_entry(entry_id, translations, category, aliases)
            flash(i18n.translate('Entrée mise à jour.'), 'success')
            return redirect(url_for('lexique.admin'))
        except Exception as e:
            flash(i18n.translate('Erreur: {}').format(str(e)), 'danger')
    
    return render_template('lexique/entry_form.html', entry=entry, 
                         languages=Config.SUPPORTED_LANGUAGES)

@lexique_bp.route('/admin/entry/<int:entry_id>/delete', methods=['POST'])
@login_required
@super_admin_required
def delete_entry(entry_id):
    try:
        LexiqueService.delete_entry(entry_id)
        flash(i18n.translate('Entrée supprimée.'), 'success')
    except Exception as e:
        flash(i18n.translate('Erreur: {}').format(str(e)), 'danger')
    
    return redirect(url_for('lexique.admin'))
