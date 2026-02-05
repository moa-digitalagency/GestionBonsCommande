import io
import csv
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import current_user, login_required
from models import db
from models.lexique import LexiqueEntry, LexiqueSuggestion
from security.decorators import super_admin_required, tenant_required
from services.lexique_service import LexiqueService
from services.i18n_service import i18n
from config.settings import Config

lexique_bp = Blueprint('lexique', __name__)

@lexique_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        category = request.form.get('category', 'general')
        translations = {}

        # Collect translations from form (expecting keys like 'term_fr', 'term_ar', etc.)
        for lang in Config.SUPPORTED_LANGUAGES:
            val = request.form.get(f'term_{lang}', '').strip()
            if val:
                translations[lang] = val

        # Basic Validation
        if not translations.get('fr'):
             flash(i18n.translate('Le terme en français est obligatoire.'), 'danger')
        else:
            try:
                # If Super Admin, add directly
                if current_user.role == 'super_admin':
                    LexiqueService.add_entry(translations, category, [])
                    flash(i18n.translate('Terme ajouté avec succès.'), 'success')
                else:
                    # Else, suggest
                    LexiqueService.suggest_term(
                        original_term=translations['fr'],
                        suggested_translations=translations,
                        category=category,
                        context="Ajout rapide via dictionnaire",
                        source_language='fr'
                    )
                    flash(i18n.translate('Suggestion envoyée pour validation.'), 'info')
            except Exception as e:
                flash(i18n.translate('Erreur lors de l\'ajout: {}').format(str(e)), 'danger')

        return redirect(url_for('lexique.index'))

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

@lexique_bp.route('/admin/import', methods=['POST'])
@login_required
@super_admin_required
def bulk_import():
    if 'file' not in request.files:
        flash(i18n.translate('Aucun fichier sélectionné.'), 'danger')
        return redirect(url_for('lexique.admin'))

    file = request.files['file']
    if file.filename == '':
        flash(i18n.translate('Aucun fichier sélectionné.'), 'danger')
        return redirect(url_for('lexique.admin'))

    if not file.filename.endswith('.csv'):
        flash(i18n.translate('Seuls les fichiers CSV sont acceptés.'), 'danger')
        return redirect(url_for('lexique.admin'))

    try:
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.DictReader(stream)

        count = 0
        for row in csv_input:
            # Expected columns: fr, en, es, ar, category
            translations = {}
            for lang in Config.SUPPORTED_LANGUAGES:
                if lang in row and row[lang].strip():
                    translations[lang] = row[lang].strip()

            if not translations.get('fr'):
                continue

            category = row.get('category', 'general')

            # Create suggestion to be validated
            suggestion = LexiqueService.suggest_term(
                original_term=translations['fr'],
                suggested_translations=translations,
                category=category,
                context="Import en masse",
                source_language='fr'
            )
            count += 1

        flash(i18n.translate('{} termes importés dans la file de validation.').format(count), 'success')

    except Exception as e:
        current_app.logger.error(f"Import Error: {e}")
        flash(i18n.translate('Erreur lors de l\'import: {}').format(str(e)), 'danger')

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
