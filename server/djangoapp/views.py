from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect, reverse
from .models import CarModel
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf , get_dealer_by_id_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.
def index(request):
    return render(request, "static/index.html")

# Create an `about` view to render a static about page
def about(request):
    return render(request, "djangoapp/about.html")

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
            return render(request, 'djangoapp/user_login.html', context)
    else:
        return render(request, 'djangoapp/user_login.html', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    # Get the user object based on session id in request
    print("Log out the user `{}`".format(request.user.username))
    # Logout user in the request
    logout(request)
    # Redirect user back to home page
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
            # Login the user and redirect to home page
            login(request, user)
            return redirect("djangoapp:index")
        else:
            return render(request, 'djangoapp/registration.html', context)


# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        context = {}
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/52484a56-0e73-495c-bfbc-23c4b6b60500/dealership-package/get-dealership.json"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name

        context['dealers'] = dealerships
        # Return a list of dealer short name
        return render(request, 'djangoapp/dealers.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
def get_dealer_details(request, dealer_id):

    if request.method == "GET":
        context={}
        # TODO update URL below
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/52484a56-0e73-495c-bfbc-23c4b6b60500/dealership-package/get-review.json"
        url2 = "https://us-south.functions.appdomain.cloud/api/v1/web/52484a56-0e73-495c-bfbc-23c4b6b60500/dealership-package/get-dealership.json"
        context['dealer_reviews'] = get_dealer_reviews_from_cf(url, id=dealer_id)
        context['dealer'] = get_dealer_by_id_from_cf(url2, id=dealer_id)
        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    context={}
    url = "https://us-south.functions.appdomain.cloud/api/v1/web/52484a56-0e73-495c-bfbc-23c4b6b60500/dealership-package/get-dealership.json"
    if request.method == 'GET':
        context['cars'] = CarModel.objects.all().filter(dealer_id=dealer_id)
        context['dealer'] = get_dealer_by_id_from_cf(url, id=dealer_id)
        return render(request, 'djangoapp/add_review.html', context)

    elif request.method == "POST":
        post_review = dict()
        json_payload = dict()

        # return HttpResponse(request.POST.items())
        purchase = request.POST.get('purchase',False)
        purchase_date = request.POST['purchase_date']
        car_id = request.POST['model']
        review = request.POST['review']
        
        post_review["purchase"] = False
        post_review["car_make"] = ""
        post_review["car_model"] = ""
        post_review["car_year"] = ""

        if purchase == "on":
            purchase = True
            post_review["purchase"] = purchase
        
        

        if(car_id != "") :
            car = get_object_or_404(CarModel,pk=car_id)
            post_review["car_make"] = car.make.name
            post_review["car_model"] = car.name
            post_review["car_year"] = car.year.strftime("%Y")

        post_review["time"] = datetime.utcnow().isoformat()
        post_review["dealership"] = dealer_id
        post_review["purchase_date"] = purchase_date
        post_review["review"] = review
        post_review["name"] = request.user.first_name + ' ' + request.user.last_name
        

        json_payload['review'] = post_review

        url = "https://us-south.functions.appdomain.cloud/api/v1/web/52484a56-0e73-495c-bfbc-23c4b6b60500/dealership-package/save-review-sequence.json"
        
        resp = post_request(url,json_payload,dealerid=dealer_id)

        print(json_payload)
        if resp['ok']:
            return redirect("djangoapp:dealer_details", dealer_id=dealer_id)

