import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions


def get_request(url,**kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        # Call get method of requests library with URL and parameters
        response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
                                    
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)

def post_request(url,json_payload,**kwargs):
    response = requests.post(url, params=kwargs, json=payload)
    return response


# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list

def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result #["rows"]
        # For each dealer object
        for dealer in dealers["entries"]:
            # Get its content in `doc` object
            dealer_doc = dealer#dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results


# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_reviews_from_cf(url, dealerId = ""):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["rows"]
        for dealer in dealers:
            dealer_doc = dealer["doc"]
            sentiment = analyze_review_sentiments(dealer_doc["review"])
            if dealer_doc["purchase"] == True:
                review_obj = DealerReview(
                    dealership = dealer_doc["dealership"],
                    name = dealer_doc["name"],
                    purchase = dealer_doc["purchase"],
                    review = dealer_doc["review"],
                    purchase_date = dealer_doc["purchase_date"],
                    car_make = dealer_doc["car_make"],
                    car_model = dealer_doc["car_model"],
                    id = dealer_doc["id"],
                    car_year = dealer_doc["car_year"] , sentiment = sentiment     
                    )
            else:
                review_obj = DealerReview(
                    dealership = dealer_doc["dealership"],
                    name = dealer_doc["name"],
                    purchase = dealer_doc["purchase"],
                    review = dealer_doc["review"],
                    id = dealer_doc["id"],
                    sentiment = sentiment      
                    )              
   
        results.append(review_obj)
        
    return results

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text

# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative

def analyze_review_sentiments(dealerreview):
    apikey = "jTpXaiMwmzYbMR1v9-uJTJb9EPG0gYXte1EQN7hBL9JW"
    url_key = "https://api.eu-gb.natural-language-understanding.watson.cloud.ibm.com/instances/7e025b1b-caf8-45cd-9307-756c56375dee"
    
    authenticator = IAMAuthenticator(apikey)
    natural_language_understanding = NaturalLanguageUnderstandingV1(
        version='2021-08-01',
        authenticator=authenticator
    )
    
    natural_language_understanding.set_service_url(url_key)
    
    response = natural_language_understanding.analyze(
        text = dealerreview,
        features=Features(sentiment=SentimentOptions())).get_result()
    
    return response["sentiment"]["document"]["label"]

