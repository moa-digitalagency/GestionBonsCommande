# /* * Nom de l'application : BTP Commande
#  * Description : Service de génération de PDF
#  * Produit de : MOA Digital Agency, www.myoneart.com
#  * Fait par : Aisance KALONJI, www.aisancekalonji.com
#  * Auditer par : La CyberConfiance, www.cyberconfiance.com
#  */

import os
from datetime import datetime
from flask import render_template, current_app

try:
    from weasyprint import HTML, CSS, default_url_fetcher
except OSError as e:
    # Capture missing system dependency errors (like pango)
    print("CRITICAL ERROR: WeasyPrint system dependencies are missing.")
    print("Please run './setup_vps.sh' (on Linux VPS) or install the required libraries.")
    print(f"Error details: {e}")
    # Re-raise to stop execution if essential, or mock if we want soft failure (but here we need it)
    raise ImportError(f"WeasyPrint system dependencies missing: {e}. Run ./setup_vps.sh") from e

class PDFService:
    @staticmethod
    def safe_url_fetcher(url, timeout=10, ssl_context=None):
        """
        Security: Custom URL fetcher to prevent LFI (Local File Inclusion).
        Only allows access to files within the static folder.
        """
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
        
        css = CSS(string='''
            @page {
                size: A4;
                margin: 1.5cm;
            }
            body {
                font-family: Arial, sans-serif;
                font-size: 11pt;
                line-height: 1.4;
            }
            .header {
                display: flex;
                justify-content: space-between;
                border-bottom: 2px solid #333;
                padding-bottom: 15px;
                margin-bottom: 20px;
            }
            .logo {
                max-height: 80px;
                max-width: 200px;
            }
            .company-info {
                text-align: right;
                font-size: 10pt;
            }
            .company-name {
                font-size: 14pt;
                font-weight: bold;
                color: #2563eb;
            }
            .bc-title {
                text-align: center;
                font-size: 18pt;
                font-weight: bold;
                margin: 20px 0;
                color: #1e40af;
            }
            .bc-number {
                text-align: center;
                font-size: 14pt;
                margin-bottom: 20px;
            }
            .info-section {
                display: flex;
                justify-content: space-between;
                margin-bottom: 20px;
            }
            .info-box {
                width: 48%;
                border: 1px solid #ddd;
                padding: 10px;
                border-radius: 5px;
            }
            .info-box h3 {
                margin: 0 0 10px 0;
                font-size: 12pt;
                color: #374151;
                border-bottom: 1px solid #ddd;
                padding-bottom: 5px;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }
            th {
                background-color: #2563eb;
                color: white;
                padding: 10px;
                text-align: left;
                font-size: 10pt;
            }
            td {
                border: 1px solid #ddd;
                padding: 8px;
                font-size: 10pt;
            }
            tr:nth-child(even) {
                background-color: #f9fafb;
            }
            .total-row {
                font-weight: bold;
                background-color: #e5e7eb !important;
            }
            .footer {
                margin-top: 30px;
                border-top: 1px solid #ddd;
                padding-top: 15px;
                font-size: 9pt;
                color: #6b7280;
            }
            .legal-info {
                margin-bottom: 10px;
            }
            .signature-section {
                display: flex;
                justify-content: space-between;
                margin-top: 40px;
            }
            .signature-box {
                width: 45%;
                border-top: 1px solid #333;
                padding-top: 10px;
                text-align: center;
            }
            .notes {
                background-color: #fffbeb;
                border: 1px solid #fbbf24;
                padding: 10px;
                border-radius: 5px;
                margin: 15px 0;
            }
        ''')
        
        uploads_dir = os.path.join(current_app.root_path, 'statics', 'uploads', 'pdfs')
        os.makedirs(uploads_dir, exist_ok=True)
        
        filename = f"BC_{order.bc_number.replace('-', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(uploads_dir, filename)
        
        # Use custom url_fetcher for security
        html = HTML(string=html_content, base_url=current_app.root_path, url_fetcher=PDFService.safe_url_fetcher)
        html.write_pdf(filepath, stylesheets=[css])
        
        relative_path = os.path.join('statics', 'uploads', 'pdfs', filename)
        
        return relative_path
    
    @staticmethod
    def get_pdf_path(order):
        if order.pdf_path:
            return os.path.join(current_app.root_path, order.pdf_path)
        return None
