from flask import Flask, request, Response, jsonify
import requests
import io
import hashlib
import PyPDF2
import base64

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
        response = requests.get(url,headers=headers,timeout=30)
        print(url)
        # print(response.text)
        
        # Return the content of the response
        return jsonify({"content": response.text, "status_code": response.status_code})
    except requests.exceptions.RequestException as e:
        # Handle any errors that occur during the request
        print(e)
        return str(e), 500
    
@app.route('/get-hash', methods=['POST'])
def get_hash():

    data = request.get_json()
    url = data.get('url')  
    headers = data.get('headers')
    try:
        algorithm = data.get('algorithm')
        buffer_size = data.get('buffer_size')
    except:
        algorithm = "sha256"
        buffer_size = 8192

    if not url:
        return "No URL provided", 400
    
    try:
        hash_function = hashlib.new(algorithm)
        # Fetch the file from the URL in chunks and update the hash
        with requests.get(url, headers=headers, timeout=30, stream=True) as response:
            # Raise an exception for bad responses
            response.raise_for_status()

            for chunk in response.iter_content(chunk_size=buffer_size):
                if chunk:
                    hash_function.update(chunk)

        # Return the hexadecimal representation of the hash
        return jsonify({"hash": hash_function.hexdigest(), "status_code": response.status_code})
    except requests.exceptions.RequestException as e:
        # Handle any errors that occur during the request
        print(e)
        return str(e), 500
    
@app.route('/proxy-stream', methods=['POST'])
def proxy_stream():

    data = request.get_json()
    url = data.get('url')  
    page_count = data.get('page_count', None)
    headers = data.get('headers')

    if not url:
        return "No URL provided", 400
    
    try:
        # Send a GET request to the URL
        response = requests.get(url,headers=headers,timeout=30,stream=True)
        print(url)
        # print(response.text)

        # Using PyPDF2 to read the PDF content
        pdf_file = io.BytesIO(response.content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        if page_count != None:
            num_pages = min(int(page_count), len(pdf_reader.pages))
        else:
            num_pages = len(pdf_reader.pages)

        text = ""
        for page_num in range(num_pages):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
        
        # Return the content of the response
        return jsonify({"num_pages": num_pages, "text": text, "status_code": response.status_code})
    except Exception as e:
        # Handle any errors that occur during the request
        print(e)
        return str(e), 500
    

@app.route('/proxy-content', methods=['POST'])
def proxy_content():

    data = request.get_json()
    url = data.get('url')  
    headers = data.get('headers')

    if not url:
        return "No URL provided", 400
    
    try:
        # Send a GET request to the URL
        response = requests.get(url,headers=headers,timeout=30)
        print(url)
        # print(response.text)

        # Encode the content in base64
        encoded_content = base64.b64encode(response.content).decode('utf-8')
        
        # Return the content of the response
        return jsonify({"content": encoded_content, "status_code": response.status_code})
    except requests.exceptions.RequestException as e:
        # Handle any errors that occur during the request
        print(e)
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True)
