from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarDealer, CarMake, CarModel
from .restapis import get_dealers_from_cf, get_request, get_dealer_reviews_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json
from django.shortcuts import get_object_or_404


# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.
def static_(request):
    return render(request,'djangoapp/index.html')

# Create an `about` view to render a static about page
def about(request):
    return render(request, 'djangoapp/about.html')

def review(request):
    return render(request, 'djangoapp/add_review.html')


# Create a `contact` view to return a static contact page
def contact(request):
    return render(request, "djangoapp/contact.html")

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    # Handles POST request
    if request.method == "POST":
        # Get username and password from request.POST dictionary
        username = request.POST['username']
        password = request.POST['psw']
        # Try to check if provide credential can be authenticated
        user = authenticate(username=username, password=password)
        if user is not None:
            # If user is valid, call login method to login current user
            login(request, user)
            return redirect('djangoapp:index')
        else:
            # If not, return to login page again
            return render(request, 'djangoapp/index.html', context)
    else:
        return render(request, 'djangoapp/index.html', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    # Get the user object based on session id in request
    print("Log out the user `{}`".format(request.user.username))
    # Logout user in the request
    logout(request)
    # Redirect user back to course list view
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    # If it is a GET request, just render the registration page
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    # If it is a POST request
    elif request.method == 'POST':
        # Get user information from request.POST
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            # Check if user already exists
            User.objects.get(username=username)
            user_exist = True
        except:
            # If not, simply log this is a new user
            logger.debug("{} is new user".format(username))
        # If it is a new user
        if not user_exist:
            # Create user in auth_user table
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            # Login the user and redirect to course list page
            login(request, user)
            return redirect("djangoapp:index")
        else:
            return render(request, 'djangoapp/registration.html', context)


# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}
    if request.method == "GET":
        #url = "your-cloud-function-domain/dealerships/dealer-get"
        url = "https://service.eu.apiconnect.ibmcloud.com/gws/apigateway/api/900338236e1f060e0903280ceee4fe2abc23403d0ae6ebe5ac1cb6e685ddbf25/api/dealership_seq"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        context["dealership_list"] = dealerships
        # Concat all dealer's short name
        dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        
        return render(request, 'djangoapp/index.html', context=context)

# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealerId):
    context = {}
    url = "https://d7967b35.eu-gb.apigw.appdomain.cloud/api/getAllRevies"
    reviews_obj = get_dealer_reviews_from_cf(url, dealerId) 
    #reviews = ' '.join(["Review : " + review.review + " => sentiment : " +  review.sentiment + "<br>" for review in reviews_obj])
    context["reviews_list"] = reviews_obj
    context["dealerId"] = dealerId

    return render(request, 'djangoapp/dealer_details.html', context)
# ...

# Create a `add_review` view to submit a review
def add_review(request, dealerId):
    #url = "https://d7967b35.eu-gb.apigw.appdomain.cloud/api/write_review_py"
    url = "https://d7967b35.eu-gb.apigw.appdomain.cloud/apitest/post_review_seq"

    #url_get_dealer_id = "https://service.eu.apiconnect.ibmcloud.com/gws/apigateway/api/900338236e1f060e0903280ceee4fe2abc23403d0ae6ebe5ac1cb6e685ddbf25/api/dealership_seq"
    # Get dealers from the URL
    context = {}
    context["dealerId"] = dealerId

    #if request.user.is_authenticated():
    if request.method == 'GET':
        context["CarModel"] = CarModel.objects.filter(id = dealerId)
        return render(request, 'djangoapp/add_review.html', context = context)
    if request.method == 'POST':
        json_payload = dict()
        review = dict()
        #review["id"] = dealerId,
        #review["name"] = request.POST["name"]
        #review["dealership"] = request.POST["dealership"]
        #review["review"] = request.POST["content"]
        #review["purchase"] = request.POST["purchase"]
        #review["purchase_date"] = datetime.utcnow().isoformat()
        #review["car_make"] = request.POST["car_make"]
        #review["car_model"] = request.POST["car_model"]
        #review["car_year"] = request.POST["car_year"]
        
        review["id"] = dealerId
        review["review"] = request.POST["content"]
        car = request.POST["car"]
        model = car.split("-")[0]
        make = car.split("-")[1]
        year = car.split("-")[2]
        review["car_model"] = model
        review["car_make"] = make
        review["car_year"] = year
        review["purchase"] = request.POST["purchasecheck"]
        review["purchase_date"] = request.POST["purchasedate"]


        review["review_time"] = datetime.utcnow().isoformat() #datetime.now()
        #year_ = datetime.strptime(request.POST["purchasedate"], "%Y/%m/%d")
        #review["car_year"] =  year_.strftime("%Y")

        json_payload["review"] = review
        response = post_request(url,review,dealerId=dealerId)

        return redirect("djangoapp:get_dealer_details", dealerId=dealerId)

        #HttpResponse(str(dealerId) + "<br>"  + json.dumps(request.POST) + "<br>" + json.dumps(review))#+ "<br>" + context["CarModel"][car].name+"-"+context["CarModel"][car].carmakes.name+"-")#+context["CarModel"][car].year )
        #redirect("djangoapp:get_dealer_details", dealerId=dealerId)

         #HttpResponse(str(dealerId) + "<br>"  + json.dumps(request.POST) + "<br>" + json.dumps(review))#+ "<br>" + context["CarModel"][car].name+"-"+context["CarModel"][car].carmakes.name+"-")#+context["CarModel"][car].year )
        #redirect("djangoapp:get_dealer_details", dealerId=dealerId)
                #HttpResponse(str(dealerId) + "<br>"+ review["review"]) 
                #render(request, 'djangoapp/add_review.html', context = context)#HttpResponse(response)#HttpResponse(review["name"] + "<br>" + review["review"]) #HttpResponse(response)
                #redirect("djangoapp:get_dealer_details")
                #redirect("djangoapp:dealer_details", dealer_id=dealerId)
