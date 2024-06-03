from django.shortcuts import render, redirect
from .forms import PlaceOrderForm
from .models import Order

def place_order(request):
    if request.method == 'POST':
        form = PlaceOrderForm(request.POST, request.FILES)
        if form.is_valid():
            # Process each uploaded file
            files = request.FILES.getlist('docfile')
            for file in files:
                handle_uploaded_file(file)
                
            # Process the other form fields
            no_of_copies = form.cleaned_data['no_of_copies']
            black_and_white = form.cleaned_data['black_and_white']
            shopkeeper_email = form.cleaned_data['shopkeeper_email']
            
            # Create an Order object and save it to the database
            order = Order(
                no_of_copies=no_of_copies,
                black_and_white=black_and_white,
                shopkeeper_email=shopkeeper_email
            )
            order.save()
            
            return redirect('success')  # Redirect to a success page
    else:
        form = PlaceOrderForm()
    
    return render(request, 'place_order.html', {'form': form})

def handle_uploaded_file(file):
    # Example function to handle each file
    with open(f'some_path/{file.name}', 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
