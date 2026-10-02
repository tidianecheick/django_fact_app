from decimal import Decimal
import datetime

# Modules de gestion des vues et des requêtes HTTP Django
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.urls import reverse
from django.views import View

# Modules de notification flash et de gestion des transactions base de données
from django.contrib import messages
from django.db import transaction

# Modèles de l'application
from .models import Customer, Invoice, Article

# Fonctions utilitaires (pagination, génération de PDF, récupération sécurisée)
from .utils import pagination, get_invoice, get_current_user, generate_pdf


# ==============================================================================
# VUE 1 : ACCUEIL ET LISTE DES FACTURES (HomeView)
# ==============================================================================
class HomeView(View):
    """
    Cette vue gère la page principale de l'application :
    - GET  : Affiche la liste des factures paginées avec tri antéchronologique.
    - POST : Traite les actions rapides (changement du statut payé / suppression).
    """
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        """
        Récupère dynamiquement toutes les factures depuis la base de données.
        'select_related' permet d'optimiser les requêtes SQL en joignant 
        les tables Customer et User en une seule requête.
        """
        # Récupération des factures triées de la plus récente à la plus ancienne
        invoices = Invoice.objects.select_related('customer', 'save_by').all().order_by('-invoice_date_time')
        
        # Découpage des résultats en pages de 5 éléments
        items = pagination(request, invoices)
        
        # Rendu du gabarit avec la liste paginée
        return render(request, self.template_name, {'invoices': items})

    def post(self, request, *args, **kwargs):
        """
        Gère les soumissions de formulaires depuis la page d'accueil :
        1. Modification de l'état de paiement (Payé / Impayé).
        2. Suppression définitive d'une facture.
        Après traitement, une redirection évite la resoumission accidentelle du formulaire.
        """
        # --- BLOC 1 : Modification de l'état de paiement ---
        if request.POST.get('id_modified'):
            paid = request.POST.get('modified')
            try:
                # Récupération de la facture ciblée par son identifiant
                obj = Invoice.objects.get(id=request.POST.get('id_modified'))
                # Conversion de la valeur reçue ("True" / "False") en booléen Python
                obj.paid = (paid == 'True')
                obj.save(update_fields=['paid'])
                messages.success(request, "Statut de paiement modifié avec succès.")
            except Exception as e:
                messages.error(request, f"Une erreur s'est produite lors de la modification : {e}")

        # --- BLOC 2 : Suppression d'une facture ---
        if request.POST.get('id_supprimer'):
            try:
                # Récupération et suppression de la facture (la suppression en cascade efface aussi les articles liés)
                obj = Invoice.objects.get(pk=request.POST.get('id_supprimer'))
                obj.delete()
                messages.success(request, "Facture supprimée avec succès.")
            except Exception as e:
                messages.error(request, f"Une erreur s'est produite lors de la suppression : {e}")

        # Pattern Post-Redirect-Get : recharge la page d'accueil proprement
        return redirect('home')


# ==============================================================================
# VUE 2 : AJOUT D'UN NOUVEAU CLIENT (AddCustomerView)
# ==============================================================================
class AddCustomerView(View):
    """
    Cette vue permet d'ajouter un nouveau client :
    - GET  : Affiche le formulaire de saisie des coordonnées du client.
    - POST : Valide les données, crée le client en base, et redirige vers l'accueil.
    """
    template_name = 'add_customer.html'

    def get(self, request, *args, **kwargs):
        """Affiche simplement le formulaire vide d'enregistrement client."""
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        """
        Récupère les informations saisies dans le formulaire,
        résout l'utilisateur connecté ou l'administrateur par défaut,
        et enregistre le nouveau client.
        """
        # Récupère l'utilisateur connecté ou un utilisateur système par défaut
        user = get_current_user(request)

        # Construction du dictionnaire des données client
        data = {
            'name': request.POST.get('name', '').strip(),
            'email': request.POST.get('email', '').strip(),
            'phone': request.POST.get('phone', '').strip(),
            'address': request.POST.get('address', '').strip(),
            'sex': request.POST.get('sex', '').strip(),
            'age': request.POST.get('age', '').strip(),
            'city': request.POST.get('city', '').strip(),
            'zip_code': request.POST.get('zip', '').strip(),
            'save_by': user,
        }

        try:
            # Création effective du client dans la base de données
            Customer.objects.create(**data)
            messages.success(request, "Client enregistré avec succès.")
            return redirect('home')
        except Exception as e:
            # En cas d'erreur (champs invalides, etc.), affiche un message et réaffiche le formulaire
            messages.error(request, f"Erreur lors de l'enregistrement du client : {e}")
            return render(request, self.template_name)


# ==============================================================================
# VUE 3 : ENREGISTREMENT ET TÉLÉCHARGEMENT DE FACTURE (AddInvoiceView)
# ==============================================================================
class AddInvoiceView(View):
    """
    Cette vue orchestre la création d'une nouvelle facture avec ses lignes d'articles :
    - GET  : Affiche le formulaire avec la liste à jour des clients disponibles.
    - POST : Valide les données, crée la facture, crée les articles en bloc (bulk_create),
             et propose deux actions :
             a) "save"               -> Enregistre et redirige vers la vue détaillée.
             b) "save_and_download"  -> Enregistre et déclenche le téléchargement immédiat du PDF.
    """
    template_name = 'add_invoice.html'

    def get(self, request, *args, **kwargs):
        """Charge la liste des clients à chaque requête GET pour garantir des données fraîches."""
        customers = Customer.objects.all().order_by('name')
        return render(request, self.template_name, {'customers': customers})

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """
        Traite la création de la facture et de ses articles de façon atomique
        (si une erreur survient au niveau des articles, la facture n'est pas créée à moitié).
        """
        # Récupération de l'action choisie par l'utilisateur
        action = request.POST.get('action', 'save')  # 'save' ou 'save_and_download'
        
        # Données principales de la facture
        customer_id = request.POST.get('customer')
        invoice_type = request.POST.get('invoice_type')
        total_val = request.POST.get('total')
        comment = request.POST.get('comment', '').strip()

        # Listes dynamiques d'articles envoyées par les champs répétables du formulaire
        articles = request.POST.getlist('article')
        qties = request.POST.getlist('qty')
        units = request.POST.getlist('unit')

        # --- VALIDATION PRÉALABLE ---
        if not customer_id:
            messages.error(request, "Veuillez sélectionner un client.")
            customers = Customer.objects.all().order_by('name')
            return render(request, self.template_name, {'customers': customers})

        if not invoice_type:
            messages.error(request, "Veuillez choisir un type de facture valide.")
            customers = Customer.objects.all().order_by('name')
            return render(request, self.template_name, {'customers': customers})

        try:
            # 1. Résolution de l'auteur de l'enregistrement
            user = get_current_user(request)

            # 2. Création de l'entité Invoice
            invoice = Invoice.objects.create(
                customer_id=customer_id,
                save_by=user,
                total=Decimal(total_val or '0'),
                invoice_type=invoice_type,
                comments=comment
            )

            # 3. Parcours et instanciation de chaque ligne d'article
            items = []
            computed_total = Decimal('0')
            for index, article_name in enumerate(articles):
                name = article_name.strip()
                if not name:
                    continue  # Ignore les lignes vides

                # Extraction sécurisée de la quantité et du prix unitaire
                qty = int(float(qties[index])) if index < len(qties) and qties[index] else 1
                unit_price = Decimal(units[index]) if index < len(units) and units[index] else Decimal('0')
                line_total = Decimal(qty) * unit_price
                computed_total += line_total

                # Création de l'objet Article associé à la facture courante
                items.append(Article(
                    invoice=invoice,
                    name=name,
                    quantity=qty,
                    unit_price=unit_price,
                    total=line_total
                ))

            # 4. Enregistrement groupé (bulk_create) des articles pour une performance optimale
            if items:
                Article.objects.bulk_create(items)
                
                # Mise à jour du total calculé si le total transmis était nul ou absent
                if computed_total > 0 and (not total_val or Decimal(total_val) == 0):
                    invoice.total = computed_total
                    invoice.save(update_fields=['total'])

            messages.success(request, f"Facture #{invoice.id} enregistrée avec succès.")

            # 5. GESTION DU TÉLÉCHARGEMENT DIRECT
            # Si l'utilisateur a cliqué sur 'Enregistrer & Télécharger PDF' :
            # Redirection vers la vue avec le paramètre ?download=1 qui déclenche
            # automatiquement le téléchargement du fichier PDF sans quitter la page.
            if action == 'save_and_download':
                return redirect(f"{reverse('view-invoice', kwargs={'pk': invoice.id})}?download=1")
            
            # Sinon, redirection classique vers la page de visualisation de la facture
            return redirect('view-invoice', pk=invoice.id)

        except Exception as e:
            # Gestion d'erreur avec message clair pour l'utilisateur
            messages.error(request, f"Désolé, une erreur s'est produite lors de l'enregistrement : {e}")
            customers = Customer.objects.all().order_by('name')
            return render(request, self.template_name, {'customers': customers})


# ==============================================================================
# VUE 4 : VISUALISATION DÉTAILLÉE DE LA FACTURE (InvoiceVisualizationView)
# ==============================================================================
class InvoiceVisualizationView(View):
    """
    Cette vue affiche le récapitulatif complet d'une facture spécifique :
    - Coordonnées de l'émetteur et du client.
    - Tableau détaillé des articles et sous-totaux.
    - Montant global et badge de statut de règlement.
    - Boutons d'actions : Télécharger PDF, Imprimer, Revenir à la liste.
    """
    template_name = 'invoice.html'

    def get(self, request, *args, **kwargs):
        # Récupère l'identifiant (clé primaire) passé dans l'URL
        pk = kwargs.get('pk')
        
        # Récupère l'objet facture et tous ses articles associés via get_invoice()
        context = get_invoice(pk)
        
        # Rendu de la page de consultation
        return render(request, self.template_name, context)


# ==============================================================================
# VUE 5 : GÉNÉRATION ET TÉLÉCHARGEMENT DU DOCUMENT PDF (get_invoice_pdf)
# ==============================================================================
def get_invoice_pdf(request, *args, **kwargs):
    """
    Vue fonctionnelle dédiée au téléchargement direct du PDF :
    1. Récupère la facture et ses articles.
    2. Injecte la date du jour pour l'impression.
    3. Rend le gabarit 'invoice_pdf.html' en PDF binaire via xhtml2pdf.
    4. Retourne une réponse HTTP avec l'en-tête 'attachment' pour forcer
       le téléchargement du fichier sur la machine de l'utilisateur.
    """
    pk = kwargs.get('pk')
    
    # 1. Récupération des données de la facture
    context = get_invoice(pk)
    context['today'] = datetime.date.today()

    # 2. Rendu du PDF à partir du template HTML print-ready
    pdf_content = generate_pdf('invoice_pdf.html', context)
    
    # 3. Si le PDF a été généré avec succès
    if pdf_content:
        response = HttpResponse(pdf_content, content_type='application/pdf')
        # Définition du nom du fichier téléchargé : facture_<NomClient>_<ID>.pdf
        customer_slug = context['obj'].customer.name.replace(' ', '_')
        filename = f"facture_{customer_slug}_{pk}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    else:
        # En cas d'erreur de rendu, message d'alerte et redirection vers la consultation
        messages.error(request, "Une erreur est survenue lors de la génération du document PDF.")
        return redirect('view-invoice', pk=pk)