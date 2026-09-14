from django.shortcuts import render, redirect 
from django.views import View
from .models import *
from django.contrib import messages
from django.db import transaction

# Create your views here.
class HomeView(View):
    
    templates_name = 'index.html'

    invoices = Invoice.objects.select_related('customer', 'save_by').all()

    context = {
        'invoices':invoices
    }

    def get (self, request, *args, **kwargs):
        
        return render(request, self.templates_name, self.context)

    def post (self, request, *args, **kwargs):
        return render(request, self.templates_name, self.context) 


class AddCustomerView(View):
    """ add customer"""
    template_name = 'add_customer.html'

    def get(self,request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs ):
        # print(request.POST) : afficher les donnnées récuperer 
        data = {
            'name':request.POST.get('name'),
            'email':request.POST.get('email'),
            'phone' : request.POST.get('phone'),
            'address' : request.POST.get('address'),
            'sex' : request.POST.get('sex'),
            'age' : request.POST.get('age'),
            'city' : request.POST.get('city'),
            'zip_code': request.POST.get('zip'),
            'save_by': request.user

        }
        try:
            created = Customer.objects.create(**data)
            messages.success(request, "Customer registered successfully")  # ← corrigé : request manquant + faute de frappe
            return redirect('liste_clients')  # ← ajouté : redirection après succès (adapter le nom de l'URL)

        except Exception as e:
            messages.error(request, f"Sorry, our system detected the following issue: {e}")  # ← corrigé : f-string manquante
            return render(request, self.template_name)  # ← réaffiche le formulaire seulement en cas d'erreu
        
        """ try:
            created = Customer.objects.create(** data)
            if created:

                messages.success("request,Customer registered succefully")

            else:
                messages.error("sorry, please try again the send data is corrupt")


        except Exception as e:
            messages.error(request ,"sorry our system is detecting the following issues {e}") 
        return render(request, self.template_name) """

""" class AddInvoiceView(View):
     la vue facture
    add a new invoice view
   
    template_name = 'add_invoice.html'

    customers = Customer.objects.select_related('save_by').all()

    context = {
        'customers' : customers
    }

    def get(self, request, *args, **kwargs):
        return render(request,self.template_name, self.context)

@transaction.atomic
def post(self, request, *args, **kwargs):

    items = []


    try:
        customer = request.POST.get('customer')
        invoice_type = request.POST.get('invoice_type')
        articles = request.POST.getlist('article')
        qties = request.POST.getlist('qty')
        units = request.POST.getlist('unit_price')
        total_a = request.POST.getlist('total_article')
        total = request.POST.get('total')
        comment = request.POST.get('comment')

        invoice_object = {
            'customer_id': customer,
            'save_by': request.user,
            'total': total,
            'invoice_type': invoice_type,
            'comments': comment
        }
        invoice = Invoice.objects.create(**invoice_object)

        for index, article in enumerate(articles):
            data = Article(
                invoice_id=invoice.id,
                name=article,
                quantity=qties[index],
                unit_price=units[index],
                total=total_a[index],
            )
            items.append(data)

        created = Article.objects.bulk_create(items)
        if created:
            messages.success(request, "Data saved successfully.")
        else:
            messages.error(request, "Sorry, please try again the data is corrupt.")

    except Exception as e:
        messages.error(request, f"Sorry the following error has occured {e}")

    return render(request, self.template_name, self.context) """

class AddInvoiceView(View):
    """ la vue facture
    add a new invoice view
    """
    template_name = 'add_invoice.html'

    customers = Customer.objects.select_related('save_by').all()

    context = {
        'customers': customers
    }

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.context)

    @transaction.atomic
    def post(self, request, *args, **kwargs):

        items = []

        try:
            customer = request.POST.get('customer')
            invoice_type = request.POST.get('invoice_type')
            articles = request.POST.getlist('article')
            qties = request.POST.getlist('qty')
            units = request.POST.getlist('unit')
            total = request.POST.get('total')
            comment = request.POST.get('comment')

            invoice_object = {
                'customer_id': customer,
                'save_by': request.user,
                'total': total,
                'invoice_type': invoice_type,
                'comments': comment
            }
            invoice = Invoice.objects.create(**invoice_object)

            for index, article in enumerate(articles):
                quantity = float(qties[index])
                unit_price = float(units[index])
                data = Article(
                    invoice_id=invoice.id,
                    name=article,
                    quantity=quantity,
                    unit_price=unit_price,
                    total=quantity * unit_price,
                )
                items.append(data)

            created = Article.objects.bulk_create(items)
            if created:
                messages.success(request, "Data saved successfully.")
            else:
                messages.error(request, "Sorry, please try again the data is corrupt.")

        except Exception as e:
            messages.error(request, f"Sorry the following error has occured {e}")

        return render(request, self.template_name, self.context)