from flask import Flask, request, jsonify, render_template
from sujud_as_shahwi import SujudAsShahwi
from waitress import serve


app = Flask(__name__)
sujood_helper = SujudAsShahwi()

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/rules')
def rules():
    return jsonify({"rules": sujood_helper.view_all_rules()})

@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    user_input = data.get("mistake", "")
    result = sujood_helper.search_mistake(user_input)
    return jsonify({"correction": result})

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=5000, debug=True, use_reloader=False)
