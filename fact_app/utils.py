from io import BytesIO
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import Invoice, Article


# ==============================================================================
# 1. GESTION DE LA PAGINATION
# ==============================================================================
def pagination(request, invoices):
    """
    Découpe une liste de factures en plusieurs pages (5 factures par page).
    - request : Requête HTTP contenant le paramètre GET 'page'.
    - invoices : QuerySet de factures à paginer.
    Retourne l'objet 'Page' correspondant à afficher.
    """
    default_page = 1
    page = request.GET.get('page', default_page)
    items_per_page = 5
    paginator = Paginator(invoices, items_per_page)
    
    try:
        items_page = paginator.page(page)
    except PageNotAnInteger:
        # Si le numéro de page n'est pas un entier (ex: ?page=abc), afficher la page 1
        items_page = paginator.page(default_page) 
    except EmptyPage:
        # Si la page demandée est au-delà du nombre réel, afficher la dernière page
        items_page = paginator.page(paginator.num_pages)
        
    return items_page


# ==============================================================================
# 2. GESTION DE L'UTILISATEUR COURANT (SÉCURITÉ & ROBUSTESSE)
# ==============================================================================
def get_current_user(request):
    """
    Récupère l'utilisateur actuellement connecté.
    Si l'utilisateur navigue de manière anonyme (non connecté via l'administration),
    cette fonction associe le premier superutilisateur existant ou en crée un par défaut.
    Cela évite les plantages de clé étrangère (save_by ForeignKey User).
    """
    if request.user.is_authenticated:
        return request.user
    
    # Recherche du premier utilisateur disponible en base
    user = User.objects.first()
    if not user:
        # Création automatique de secours si aucun utilisateur n'existe
        user = User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    return user


# ==============================================================================
# 3. RÉCUPÉRATION SÉCURISÉE D'UNE FACTURE ET DE SES ARTICLES
# ==============================================================================
def get_invoice(pk):
    """
    Récupère une facture par son identifiant unique (clé primaire pk)
    ainsi que tous les articles qui lui sont rattachés.
    - Utilise get_object_or_404 pour renvoyer une erreur 404 propre si la facture n'existe pas.
    """
    obj = get_object_or_404(Invoice, pk=pk)
    # Récupération de tous les articles liés à cette facture
    articles = obj.article_set.all()
    context = {
        'obj': obj,
        'articles': articles,
    }
    return context


# ==============================================================================
# 4. MOTEUR DE GÉNÉRATION PDF (XHTML2PDF)
# ==============================================================================
def generate_pdf(template_name, context):
    """
    Convertit un gabarit Django (HTML + CSS) en un flux binaire PDF.
    - template_name : Chemin du fichier HTML (ex: 'invoice_pdf.html').
    - context : Dictionnaire de variables injectées dans le template (obj, articles, etc.).
    - Retourne les octets binaires du PDF en cas de succès, ou None en cas d'échec.
    """
    # 1. Chargement et rendu du gabarit HTML avec les variables fournies
    template = get_template(template_name)
    html = template.render(context)
    
    # 2. Buffer mémoire pour stocker le fichier généré
    result = BytesIO()
    
    # 3. Conversion du code HTML encodé en UTF-8 vers le format PDF
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    
    # 4. Vérification de l'absence d'erreurs
    if not pdf.err:
        return result.getvalue()
    return None