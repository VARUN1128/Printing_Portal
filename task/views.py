from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse
from .models import Order
from .forms import PlaceOrderForm
from .forms import otpForm
from django.views.generic import UpdateView
import razorpay
import random
from PyPDF2 import PdfFileMerger
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from reportlab.pdfgen import canvas 
from reportlab.pdfbase import pdfmetrics
import os
import json
from . import shopkeepers 

def customer(request):
    email = request.session['user']['email']
    all_entries = Order.objects.filter(customer_email = email,)
    return render(request, 'task/c_display.html', {'all_entries' : all_entries})

# quering into the database to find out the orders reamining to be printed by the shopkeeper
def shopkeeper(request):
       form = otpForm()
       email = request.session['user']['email']
       all_entries = Order.objects.filter(payment_status = True, collected_status = False)
       return render(request, 'task/display.html', {'all_entries':all_entries ,'form' :form})

def place_order(request):
    if request.method == 'POST':
        form = PlaceOrderForm(request.POST, request.FILES)
        if form.is_valid():
            print(shopkeepers.shops)
            shops = shopkeepers.shops
            customer_name = request.session['user']['name']
            customer_email = request.session['user']['email']

            files = request.FILES.getlist('docfile')
            
            if len(files) > 5:
                messages.warning(request,f'Please upload at most 5 PDFs.')
                return HttpResponseRedirect(reverse('place_order'))

            limit = 10*1024*1024
            for file in files :
                if file.size > limit:
                    messages.warning(request,f'File too large. Size should not exceed 10 MB.')
                    return HttpResponseRedirect(reverse('place_order'))
                if not file.name.endswith(".pdf"):
                    messages.warning(request,f'Uploading non PDF file is not allowed')
                    return HttpResponseRedirect(reverse('place_order'))  

            shop_email = form.cleaned_data.get('shopkeeper_email')
            for key in shops:
                if key == shop_email:
                    shop_location = shops[key]

            no_of_copies = form.cleaned_data.get('no_of_copies')
            black_and_white = form.cleaned_data.get('black_and_white')
            otp = random.randint(1000,10000)

            #creating extra pdf having name and email
            os.chdir(settings.MEDIA_ROOT)
            fileName = 'customer_detail.pdf'
            pdf = canvas.Canvas(fileName)
            pdf.setFont("Courier-Bold", 36)
            pdf.drawCentredString(300, 590, customer_name)
            pdf.setFont("Courier-Bold", 24)
            pdf.drawCentredString(290,500, customer_email)
            pdf.save()

            # pdf merging
            merger = PdfFileMerger()
            for file in files:
                merger.append(file)
            merger.append(fileName)
            
            all_entries = Order.objects.filter(customer_email = customer_email)
            newfile_name = customer_email + '-' + str(len(all_entries)) + '.pdf'
            num_pages = len(merger.pages)
            merger.write(newfile_name)
            merger.close()

            #calculating cost
            price_black_and_white = 1
            price_color = 5
            if black_and_white:
                cost = num_pages*price_black_and_white
            else:
                cost = num_pages*price_color
            cost = cost*no_of_copies

            neworder = Order(
                customer_name = customer_name, 
                customer_email = customer_email, 
                otp = otp, 
                shopkeeper_email = shop_email,
                shopkeeper_location = shop_location,
                docfile = newfile_name,  
                no_of_copies = no_of_copies, 
                black_and_white=black_and_white, 
                cost = cost
            )
            neworder.save()
            return HttpResponseRedirect(reverse('gateway'))
        else:
            messages.error(request,f'Form enteries are invalid')
            return redirect('home')
    else : 
        form = PlaceOrderForm()
        key = 'user'
        if key in request.session:
            return render(request,'task/place_order.html',{'form':form, 'user': request.session[key]}) 
        else:
            return redirect('home')

def gateway(request):
    if request.method== "POST":
        email = request.session['user']['email']
        order = Order.objects.filter(customer_email = email).last()
        cost = order.cost*100
        client = razorpay.Client(auth = ("rzp_test_aBF0M5yvtP4PDr", "lPodFzCQ4YXDa9l8XfYCfgB3"))
        payment = client.order.create({'amount':cost, 'currency': 'INR', 'payment_capture':'1'})
        order.payment_id = payment['id']
        order.save()
        return render(request,'task/index.html',{'payment':payment})
    return render(request,'task/index.html')

@csrf_exempt
def success(request):
    if request.method == "POST":
        a = request.POST
        print(request.session['user']['email'])
        for key, val in a.items():
            if key == "razorpay_order_id":
                order_id = val
                break
        user = Order.objects.filter(payment_id = order_id).first()
        user.payment_status = True
        user.save()
        messages.success(request,f'Your order has been placed.')
    return render(request, 'task/success.html')

#class based function expect views of the following naming convertion:
# <app>/<model>_<viewtype>.html

# but for update it expects name to be <app>/<model>_form.html 
# because it shares the template with create view

def download(request, path):
    file_path = path
    os.chdir(settings.MEDIA_ROOT)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/force-download")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    else :
        messages.warning(request,f'Document not found.')
        return redirect('shopkeeper-orders')
    
def status_change(request,path):
    transaction = Order.objects.get(payment_id = path)
    transaction.printing_status = True
    transaction.save()

    messages.success(request,f'We will inform {transaction.customer_name} that documents have been printed.')
    return redirect('shopkeeper-orders')

def validator(request,path):
    form = otpForm(request.POST)
    if form.is_valid() :
            data = form.cleaned_data
            otp = data['otp']
            transaction = Order.objects.get(payment_id = path)
            tras = Order.objects.filter(payment_id=path)
            if transaction.otp == otp:
                transaction.collected_status=True
                transaction.save()

                os.chdir(settings.MEDIA_ROOT)
                if os.path.exists(transaction.docfile.name):
                   os.remove(transaction.docfile.name)
                messages.success(request,f'{transaction.customer_name} have collected his documents.')
                return redirect('shopkeeper-orders')
            else :
                messages.warning(request,f'Wrong OTP entered.')
                return redirect('shopkeeper-orders')
    else:
        messages.error(request,f'An error occured! Please try again')
        return redirect('shopkeeper_orders')