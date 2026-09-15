from django.core.paginator import(Paginator, EmptyPage, PageNotAnInteger)

def pagination(request, invoices):
     # Default page
    default_page = 1
    page = request.GET.get('page', default_page)
    
            # Paginate items
    items_per_page = 5
    paginator = Paginator(invoices, items_per_page)
    
    try:
        items_page = paginator.page(page)
    
    except PageNotAnInteger:    
        items_page =  paginator.page(default_page) 
    
    except EmptyPage: 
    
        items_page = paginator.page(paginator.num_pages)
    return items_page