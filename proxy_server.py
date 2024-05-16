from flask import Flask, request, Response, jsonify
import requests
import io
import PyPDF2

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
    
@app.route('/proxy-stream', methods=['POST'])
def proxy_stream():

    data = request.get_json()
    url = data.get('url')  
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
        num_pages = len(pdf_reader.pages)

        text = ""
        for page_num in range(num_pages):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
        
        # Return the content of the response
        return jsonify({"num_pages": num_pages, "text": text, "status_code": response.status_code})
    except requests.exceptions.RequestException as e:
        # Handle any errors that occur during the request
        print(e)
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True)
