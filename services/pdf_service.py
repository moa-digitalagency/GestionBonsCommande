# /* * Nom de l'application : BTP Commande
#  * Description : Service de génération de PDF
#  * Produit de : MOA Digital Agency, www.myoneart.com
#  * Fait par : Aisance KALONJI, www.aisancekalonji.com
#  * Auditer par : La CyberConfiance, www.cyberconfiance.com
#  */

import os
from datetime import datetime
from flask import render_template, current_app

WEASYPRINT_AVAILABLE = False
try:
    from weasyprint import HTML, CSS, default_url_fetcher
    WEASYPRINT_AVAILABLE = True
except (OSError, ImportError) as e:
    # Capture missing system dependency errors (like pango)
    print("WARNING: WeasyPrint system dependencies are missing.")
    print("PDF generation will be disabled.")
    print("Please run './setup_vps.sh' (on Linux VPS) and ensure the virtual environment is activated.")
    print(f"Error details: {e}")
    # Define dummy classes to avoid NameErrors if referenced (though logical guards should prevent use)
    HTML = None
    CSS = None
    default_url_fetcher = None

class PDFService:
    @staticmethod
    def safe_url_fetcher(url, timeout=10, ssl_context=None):
        """
        Security: Custom URL fetcher to prevent LFI (Local File Inclusion).
        Only allows access to files within the static folder.
        """
        if not WEASYPRINT_AVAILABLE:
             raise RuntimeError("WeasyPrint is not available. Install system dependencies.")

        if url.startswith('file://'):
            path = url[7:]
            # Determine the allowed directory (static folder)
            static_folder = os.path.abspath(current_app.static_folder)
            # Normalize the requested path
            file_path = os.path.abspath(path)

            # Check if file_path is within static_folder
            # Also allow uploads folder which might be separate but usually under static
            # In this app uploads are in static/uploads

            if not file_path.startswith(static_folder):
                current_app.logger.warning(f"Security Alert: Blocked attempt to access file outside static folder: {url}")
                raise PermissionError("Access denied: File outside static folder")

        return default_url_fetcher(url, timeout=timeout, ssl_context=ssl_context)

    @staticmethod
    def generate_order_pdf(order):
        if not WEASYPRINT_AVAILABLE:
             raise RuntimeError(
                "La génération de PDF est indisponible car les dépendances système (WeasyPrint/Pango) sont manquantes. "
                "Assurez-vous que './setup_vps.sh' a été exécuté et que l'environnement virtuel est activé."
            )

        if not order.can_generate_pdf():
            if order.status not in ['PDF_GENERE', 'PARTAGE']:
                raise ValueError("Le BC doit être validé avant de générer le PDF")
        
        company = order.company
        project = order.project
        lines = order.lines.order_by('line_number').all()
        
        html_content = render_template('pdf/order_pdf.html',
            order=order,
            company=company,
            project=project,
            lines=lines,
            generated_at=datetime.utcnow()
        )
        
        css_path = os.path.join(current_app.static_folder, 'css', 'pdf.css')
        css = CSS(filename=css_path)
        
        uploads_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'pdfs')
        os.makedirs(uploads_dir, exist_ok=True)
        
        filename = f"BC_{order.bc_number.replace('-', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(uploads_dir, filename)
        
        # Use custom url_fetcher for security
        html = HTML(string=html_content, base_url=current_app.root_path, url_fetcher=PDFService.safe_url_fetcher)
        html.write_pdf(filepath, stylesheets=[css])
        
        relative_path = os.path.join('static', 'uploads', 'pdfs', filename)
        
        return relative_path
    
    @staticmethod
    def get_pdf_path(order):
        if order.pdf_path:
            return os.path.join(current_app.root_path, order.pdf_path)
        return None
