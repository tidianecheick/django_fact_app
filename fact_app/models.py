
# Create your models here.
""" class Customer(models.Model):
   
    Name: definition du model client
    customer model definition
    
    SEX_TYPES = (
        ('M', 'Masculin'),
        ('F','Feminiin'),
        )
    name = models.CharField(max_length=132)

    email = models.EmailField()

    phone = models.CharField(max_length=132)

    address = models.CharField(max_length=64)

    sex = models.CharField(max_length=1,choices=SEX_TYPES)

    age = models.CharField(max_length=12)

    city = models.CharField(max_length=32)

    zip_code = models.CharField(max_length=16)

    ceated_date = models.DateField(auto_now=True)

    save_by = models.ForeignKey(User, on_delete =models.PROTECT)

    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"

    def __str__(self):
        return self.name 

class Invoice(models.Model):
    
    Name: Invoice model definition
    definition du model facture
    Description:
    author:tidiane@gmail.com
    
    INVOICE_TYPE_CHOICES = (
        ('R','RECU'),
        ('P','PROFORMA FACTURE'),
        ('F','FACTURE'),
    )
    customer = models.ForeignKey(Customer, on_delete =models.PROTECT)

    save_by = models.ForeignKey(User, on_delete=models.PROTECT)

    invoice_date_time = models.DateTimeField(auto_now_add = True)

    total = models.DecimalField(max_digits=12, decimal_places=2)

    last_update_date = models.DateTimeField(null=True, blank=True)

    paid = models.BooleanField(default=False)

    invoice_type = models.CharField(max_length=1, choices = INVOICE_TYPE_CHOICES)

    comments = models.TextField(null=True, max_length=100, blank=True)

    class Meta:
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"

    def __str__(self):
        return f"{self.customer.name} {self.invoice_date_time}" 

    @property
    def get_total(self):
        articles = self.article_set.all()
        total = sum(article.get_total for article in articles)

class Article(models.Model):
    
    Name : Article model definition(le model qui decrit article)
    Description:
    Author:tidiane@gmail.com
    
    invoive = models.ForeignKey(Invoice,on_delete=models.CASCADE)
    name = models.CharField(max_length=32) 
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=100, decimal_places=2)
    total = models.DecimalField(max_digits=100,decimal_places=2)

    class Meta:
        verbose_name = 'Article'
        verbose_name_plural ='Articles'

    @property
    def get_total(self):
        total = self.quantity * self.unit_price
 """
from django.db import models
from django.contrib.auth.models import User


class Customer(models.Model):

    SEX_TYPES = (
        ('M', 'Masculin'),
        ('F', 'Féminin'),
    )

    name = models.CharField(max_length=132)
    email = models.EmailField()
    phone = models.CharField(max_length=132)
    address = models.CharField(max_length=64)
    sex = models.CharField(max_length=1, choices=SEX_TYPES)
    age = models.CharField(max_length=12)
    city = models.CharField(max_length=32)
    zip_code = models.CharField(max_length=16)

    created_date = models.DateTimeField(auto_now=True)

    save_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT
    )

    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"

    def __str__(self):
        return self.name


class Invoice(models.Model):

    INVOICE_TYPE_CHOICES = (
        ('R', 'RECEIPT'),
        ('P', 'PROFORMA INVOICE'),
        ('I', 'INVOICE'),
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT
    )

    save_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT
    )

    invoice_date_time = models.DateTimeField(
        auto_now_add=True
    )

    total = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    last_update_date = models.DateTimeField(
        null=True,
        blank=True
    )

    paid = models.BooleanField(default=False)

    invoice_type = models.CharField(
        max_length=1,
        choices=INVOICE_TYPE_CHOICES
    )

    comments = models.TextField(
        null=True,
        max_length=100,
        blank=True
    )

    class Meta:
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"

    def __str__(self):
        return f"{self.customer.name} {self.invoice_date_time}"

    @property
    def get_total(self):
        articles = self.article_set.all()
        if articles.exists():
            return sum(article.get_total for article in articles)
        return self.total or 0



class Article(models.Model):

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE
    )

    name = models.CharField(max_length=32)

    quantity = models.IntegerField()

    unit_price = models.DecimalField(
        max_digits=100,
        decimal_places=2
    )

    total = models.DecimalField(
        max_digits=100,
        decimal_places=2
    )

    class Meta:
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'

    @property
    def get_total(self):
        total =  self.quantity * self.unit_price
        return total
