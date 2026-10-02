from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from decimal import Decimal
from .models import Customer, Invoice, Article

class InvoiceSystemTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_superuser('admin', 'admin@example.com', 'adminpass')
        self.customer = Customer.objects.create(
            name='Alpha Services',
            email='contact@alpha.com',
            phone='70112233',
            address='Rue 12, Secteur 4',
            sex='M',
            age='26-40',
            city='Ouagadougou',
            zip_code='01 BP 500',
            save_by=self.user
        )

    def test_home_page(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Gestion des Factures')

    def test_add_customer(self):
        data = {
            'name': 'Beta SARL',
            'email': 'beta@sarl.com',
            'phone': '76543210',
            'address': 'Zone Industrielle',
            'sex': 'F',
            'age': '18-25',
            'city': 'Bobo-Dioulasso',
            'zip': 'BP 200',
        }
        response = self.client.post(reverse('add-customer'), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))
        self.assertTrue(Customer.objects.filter(name='Beta SARL').exists())

    def test_add_invoice_and_download_pdf(self):
        # 1. Enregistrement avec 'save_and_download'
        invoice_data = {
            'action': 'save_and_download',
            'customer': self.customer.id,
            'invoice_type': 'I',
            'article': ['Serveur Web Dell', 'Onduleur APC'],
            'qty': ['1', '2'],
            'unit': ['850000', '75000'],
            'total': '1000000',
            'comment': 'Installation sous 48h',
        }
        response = self.client.post(reverse('add-invoice'), invoice_data)
        self.assertEqual(response.status_code, 302)

        invoice = Invoice.objects.filter(customer=self.customer).first()
        self.assertIsNotNone(invoice)
        self.assertEqual(invoice.article_set.count(), 2)
        self.assertEqual(invoice.get_total, Decimal('1000000.00'))

        # Redirection vers la visualisation avec ?download=1
        expected_url = f"{reverse('view-invoice', kwargs={'pk': invoice.id})}?download=1"
        self.assertEqual(response.url, expected_url)

        # 2. Visualisation de la facture
        view_response = self.client.get(reverse('view-invoice', kwargs={'pk': invoice.id}))
        self.assertEqual(view_response.status_code, 200)
        self.assertContains(view_response, 'Alpha Services')
        self.assertContains(view_response, 'Serveur Web Dell')

        # 3. Téléchargement du fichier PDF
        pdf_response = self.client.get(reverse('invoice-pdf', kwargs={'pk': invoice.id}))
        self.assertEqual(pdf_response.status_code, 200)
        self.assertEqual(pdf_response['Content-Type'], 'application/pdf')
        self.assertIn('attachment;', pdf_response['Content-Disposition'])
        self.assertGreater(len(pdf_response.content), 1000)

    def test_invoice_status_update_and_delete(self):
        invoice = Invoice.objects.create(
            customer=self.customer,
            save_by=self.user,
            total=Decimal('50000'),
            invoice_type='R',
            paid=False
        )

        # Modifier le statut en Payé
        response = self.client.post(reverse('home'), {
            'id_modified': invoice.id,
            'modified': 'True'
        })
        self.assertEqual(response.status_code, 302)
        invoice.refresh_from_db()
        self.assertTrue(invoice.paid)

        # Supprimer la facture
        del_response = self.client.post(reverse('home'), {
            'id_supprimer': invoice.id
        })
        self.assertEqual(del_response.status_code, 302)
        self.assertFalse(Invoice.objects.filter(id=invoice.id).exists())
