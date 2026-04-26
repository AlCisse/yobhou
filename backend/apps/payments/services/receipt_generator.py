"""
Générateur de reçus PDF pour Yobhou
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from datetime import datetime
import io


class ReceiptGenerator:
    """Générateur de reçus de paiement"""
    
    # Couleurs Yobhou
    PRIMARY_BLUE = HexColor('#2563EB')
    DARK_NAVY = HexColor('#0F172A')
    ACCENT_GREEN = HexColor('#10B981')
    
    @classmethod
    def generate_pdf(cls, payment) -> bytes:
        """
        Générer un reçu PDF pour un paiement
        
        Args:
            payment: Instance du modèle Payment
        
        Returns:
            bytes: Contenu PDF
        """
        buffer = io.BytesIO()
        
        # Créer le PDF
        pdf = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # En-tête
        cls._draw_header(pdf, width, height)
        
        # Informations transaction
        cls._draw_transaction_details(pdf, payment, width, height)
        
        # Pied de page
        cls._draw_footer(pdf, width, height)
        
        # Finaliser
        pdf.save()
        buffer.seek(0)
        
        return buffer.getvalue()
    
    @classmethod
    def _draw_header(cls, pdf, width, height):
        """Dessiner l'en-tête du reçu"""
        # Fond bleu
        pdf.setFillColor(cls.PRIMARY_BLUE)
        pdf.rect(0, height - 40*mm, width, 40*mm, fill=True, stroke=False)
        
        # Logo Yobhou (texte pour l'instant)
        pdf.setFillColor(HexColor('#FFFFFF'))
        pdf.setFont('Helvetica-Bold', 24)
        pdf.drawString(20*mm, height - 25*mm, 'YOBHOU')
        
        # Sous-titre
        pdf.setFont('Helvetica', 12)
        pdf.drawString(20*mm, height - 35*mm, 'Paiement Facture EDG')
    
    @classmethod
    def _draw_transaction_details(cls, pdf, payment, width, height):
        """Dessiner les détails de la transaction"""
        y = height - 60*mm
        
        # Titre
        pdf.setFillColor(cls.DARK_NAVY)
        pdf.setFont('Helvetica-Bold', 16)
        pdf.drawString(20*mm, y, 'Reçu de Paiement')
        
        y -= 15*mm
        
        # Ligne de séparation
        pdf.setStrokeColor(cls.PRIMARY_BLUE)
        pdf.setLineWidth(1)
        pdf.line(20*mm, y, width - 20*mm, y)
        
        y -= 15*mm
        
        # Détails
        details = [
            ('Référence:', payment.transaction_reference),
            ('Date:', payment.created_at.strftime('%d/%m/%Y %H:%M')),
            ('Montant:', f'{payment.amount:,.0f} GNF'),
            ('Méthode:', payment.get_payment_method_display()),
            ('Numéro Compteur:', payment.meter_reading.meter_number if payment.meter_reading else 'N/A'),
            ('Statut:', 'Terminé' if payment.status == 'COMPLETED' else payment.status),
        ]
        
        pdf.setFont('Helvetica', 11)
        for label, value in details:
            pdf.setFillColor(HexColor('#6B7280'))
            pdf.drawString(20*mm, y, label)
            
            pdf.setFillColor(cls.DARK_NAVY)
            pdf.drawString(70*mm, y, str(value))
            y -= 10*mm
        
        y -= 10*mm
        
        # Message de confirmation
        pdf.setFillColor(cls.ACCENT_GREEN)
        pdf.setFont('Helvetica-Bold', 12)
        pdf.drawString(20*mm, y, '✓ Paiement confirmé')
        
        y -= 15*mm
        
        # QR Code placeholder
        pdf.setFillColor(HexColor('#F3F4F6'))
        pdf.rect(20*mm, y - 40*mm, 40*mm, 40*mm, fill=True, stroke=False)
        pdf.setFillColor(cls.DARK_NAVY)
        pdf.setFont('Helvetica', 8)
        pdf.drawString(22*mm, y - 20*mm, 'QR Code')
        pdf.drawString(22*mm, y - 25*mm, 'de vérification')
    
    @classmethod
    def _draw_footer(cls, pdf, width, height):
        """Dessiner le pied de page"""
        y = 30*mm
        
        pdf.setFillColor(HexColor('#9CA3AF'))
        pdf.setFont('Helvetica', 9)
        
        pdf.drawString(20*mm, y, 'Yobhou Fintech - Conakry, Guinée')
        pdf.drawString(20*mm, y - 5*mm, 'support@yobhou.com | www.yobhou.gn')
        pdf.drawString(20*mm, y - 10*mm, 'Licence BCEAO en cours de demande')
        
        # Numéro de page
        pdf.drawRightString(width - 20*mm, y, 'Page 1/1')
