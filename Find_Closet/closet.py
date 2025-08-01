from google import genai
import os
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
from PIL import Image
from flask import jsonify
import markdown

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    print(f"Creating {UPLOAD_FOLDER} directory.")
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index_clothes.html') 

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image_file' not in request.files:
        return 'No file part'

    file = request.files['image_file']

    if file.filename == '':
        return 'No selected file'


    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(os.path.join(os.path.dirname(__file__), 'uploads'), filename)
        
        file.save(filepath) 
        
        img = Image.open(filepath)
        
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

        types_of_clothes = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=["Can you generate each type of clothing to great detail seperated by two commas and one space? \
            Each color of the same clothing should be a seperate item. Only return the clothes nothing else. \
            Seperate each clothing item by exactly two commas and one space. No enters.", img],
        )
        
        clothes = (types_of_clothes.text.strip()).split(",, ")

        return render_template('clothes.html', clothes=clothes)

@app.route('/selected', methods=['POST'])
def selected():
    event = request.form["event"]
    selected_items = request.form.getlist("selected_clothes")
    clothing_choices = ", ".join(selected_items)
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

    response = client.models.generate_content(
        model = "gemini-2.5-flash",
        contents=[
            f"This is all the clothing choices from the closet: {clothing_choices} \
            What outfits can you suggest for a {event} event."
        ]
    )
    response = markdown.markdown(response.text)
    return render_template("selected.html", selected_items=selected_items, response=response)



if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True) 
    app.run(debug=True, host = '0.0.0.0', port=8000)