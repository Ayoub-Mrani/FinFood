from flask import Flask, request, jsonify
import requests
import json
import geocoder
import openai
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
app.debug = True
key = "REPLACE_YOUR_API_KEY_HERE"
customer_id = "REPLACE_YOUR_API_KEY_HERE"
checking_id = "REPLACE_YOUR_API_KEY_HERE"
most_freq_res = ""
curr_location = geocoder.ip('me')


@app.route("/customers")
def get_customer():
	url = f"http://api.nessieisreal.com/accounts/{customer_id}?key={key}"
	response = requests.get(url)
	data = response.json()
	# return data as a JSON response
	return data

# get_restaurents makes a GET request and retrieves a JSON response
# with the restaurant name tagged in the description

@app.route("/transactions")
def all_rest():

	url = f"http://api.nessieisreal.com/accounts/{checking_id}/purchases?key={key}"
	response = requests.get(url)
	return response.json()
	
	restr_name_to_count = dict()
	for transaction in response.json(): 
		if 'restaurant' in transaction["description"].lower():
			name = transaction["description"].split(":")[1].strip()
			count = restr_name_to_count.get(name)
			if count is None:
				restr_name_to_count[name] = 1
			else:
				restr_name_to_count[name] = count + 1
	
	most_freq_rest = max(restr_name_to_count, key=restr_name_to_count.get)
	return most_freq_rest
	

@app.route("/freq_res")
def get_freq_rest():

	url = f"http://api.nessieisreal.com/customers/{checking_id}/purchases?key={key}"
	response = requests.get(url)
	
	restr_name_to_count = dict()
	for transaction in response.json(): 
		if 'restaurant' in transaction["description"].lower():
			name = transaction["description"].split(":")[1].strip()
			count = restr_name_to_count.get(name)
			if count is None:
				restr_name_to_count[name] = 1
			else:
				restr_name_to_count[name] = count + 1
	
	most_freq_rest = max(restr_name_to_count, key=restr_name_to_count.get)
	return most_freq_rest
	
			
	# print(data)
	# # return data as a JSON response
	# return data    

@app.route("/genre")
def find_genre():
	most_freq_rest = get_freq_rest()
	yelp =  "https://api.yelp.com/v3/businesses/search"
	yelp_api_key = "h7Ibjgw_4IWYatqHflKUhwwDXvEtBr9-6D-HSiUbui8qj9Zb2fZ86fs9dKn5EyFiB2DDNUJz-DNrYwzDlpFanUFcNqGREEgM1GTnWtaHBfi-HMIzgvBs3WOp0WkfZHYx"
	headers = {"Authorization": f"Bearer {yelp_api_key}"}
	params = {"term": most_freq_rest, "location": curr_location} 
	yelp_response = requests.get(yelp, headers=headers, params=params)
	yelp_data = yelp_response.json()
	categories = yelp_data["businesses"][0]["categories"]
	category_list = []
	for category in categories:
		category_list.append(category['title'])
	return category_list
	# genre = yelp_data["businesses"][0]["categories"][0]["title"]

	# return f"The most frequent restaurant is {most_freq_res}, which is a {genre} restaurant."

@app.route("/meals")
def get_meals():
    category_list = find_genre()
    openai.api_key = "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"

    response = openai.ChatCompletion.create(
  		model="gpt-3.5-turbo",
  		messages=[
        	{"role": "user", "content": "Give me 5 meals related to these categories: " + ' '.join(category_list)}
    ]
	)
    msg = response["choices"][0]["message"]["content"]
    return msg
    # return response["choices"][0]["text"]
	

if __name__ == "__main__":
	app.run(debug=True)

