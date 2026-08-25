from django.shortcuts import render, redirect 
from django.views import View
from .models import *
from django.contrib import messages

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
