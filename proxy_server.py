from flask import Flask, request, Response, jsonify
import requests

app = Flask(__name__)

@app.route('/proxy', methods=['POST'])
def proxy():

    data = request.get_json()
    url = data.get('url')  
    headers = data.get('headers')

    if not url:
        return "No URL provided", 400
    
    try:
        # Send a GET request to the URL
        response = requests.get(url,headers=headers)
        print(url)
        # print(response.text)
        
        # Return the content of the response
        return jsonify({"content": response.text, "status_code": response.status_code})
    except requests.exceptions.RequestException as e:
        # Handle any errors that occur during the request
        print(e)
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True)
