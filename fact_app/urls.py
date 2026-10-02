from django.urls import path
from . import views

# ==============================================================================
# ROUTAGE DES URLS DE L'APPLICATION FACTURATION (fact_app)
# ==============================================================================
urlpatterns = [
    # 1. Page d'accueil : Tableau de bord et liste de toutes les factures paginées
    path('', views.HomeView.as_view(), name='home'),

    # 2. Formulaire d'enregistrement d'un nouveau client
    path('add-customer', views.AddCustomerView.as_view(), name='add-customer'),

    # 3. Formulaire de création d'une nouvelle facture (avec articles dynamiques et téléchargement immédiat)
    path('add-invoice', views.AddInvoiceView.as_view(), name='add-invoice'),

    # 4. Consultation détaillée d'une facture spécifique par son identifiant numérique (pk)
    path('view-invoice/<int:pk>', views.InvoiceVisualizationView.as_view(), name='view-invoice'),

    # 5. Téléchargement direct du fichier PDF généré de la facture
    path('invoice-pdf/<int:pk>', views.get_invoice_pdf, name='invoice-pdf'),
]