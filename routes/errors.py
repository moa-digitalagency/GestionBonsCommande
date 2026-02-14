from flask import Blueprint, render_template, abort
from config.settings import Config

errors_bp = Blueprint('errors', __name__)

@errors_bp.app_errorhandler(400)
def bad_request_error(error):
    return render_template('errors/400.html',
                           whatsapp_number=Config.WHATSAPP_NUMBER,
                           tidycal_url=Config.TIDYCAL_URL), 400

@errors_bp.app_errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html',
                           whatsapp_number=Config.WHATSAPP_NUMBER,
                           tidycal_url=Config.TIDYCAL_URL), 403

@errors_bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html',
                           whatsapp_number=Config.WHATSAPP_NUMBER,
                           tidycal_url=Config.TIDYCAL_URL), 404

@errors_bp.app_errorhandler(451)
def unavailable_for_legal_reasons_error(error):
    return render_template('errors/451.html',
                           whatsapp_number=Config.WHATSAPP_NUMBER,
                           tidycal_url=Config.TIDYCAL_URL), 451
