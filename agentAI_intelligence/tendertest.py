from flask import Flask, request, jsonify, render_template, session
import pandas as pd
# Uncomment if using GPT-4
# import openai

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Required for session management

# Load historical supplier data
historical_data_file = "historical_supplier_data.csv"
try:
    historical_supplier_data = pd.read_csv(historical_data_file).to_dict(orient="records")
    print(f"Loaded historical supplier data from {historical_data_file}")
except Exception as e:
    print(f"Error loading historical data: {e}")
    historical_supplier_data = []

# Route: Home Page
@app.route('/')
def index():
    return render_template('index.html')

# Route: Create Event
@app.route('/create_event', methods=['POST'])
def create_event():
    buyer_input = request.json

    # Effective GPT-4 prompt
    """
    prompt = f"""
    You are an AI procurement assistant. Based on the following buyer input and historical supplier data, recommend:
    1. Ranked suppliers with scores (1-100) and explanations.
    2. Advanced insights such as market trends, risks, and optimizations.

    Buyer Input:
    {buyer_input}

    Historical Supplier Data:
    {historical_supplier_data}

    Provide JSON response with rankings and insights.
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a procurement AI assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    recommendations = eval(response['choices'][0]['message']['content'])
    """

    # Mock GPT-4 response for testing
    recommendations = [
        {"name": "TechWorld", "score": 95, "explanation": "High reliability and excellent quality."},
        {"name": "DataMax", "score": 90, "explanation": "Competitive pricing and good delivery performance."},
    ]

    return jsonify({"recommendations": recommendations})

# Route: Select Suppliers
@app.route('/select_supplier', methods=['POST'])
def select_supplier():
    selected_suppliers = request.json.get("selected_suppliers", [])
    if not selected_suppliers:
        return jsonify({"error": "No suppliers selected"}), 400

    session["selected_suppliers"] = selected_suppliers
    return jsonify({"message": f"Suppliers selected: {', '.join(selected_suppliers)}"})

# Route: Submit Bid
@app.route('/submit_bid', methods=['POST'])
def submit_bid():
    bid_details = request.json
    supplier_id = bid_details.get("supplier_id")
    if not supplier_id:
        return jsonify({"error": "Supplier ID is required"}), 400

    session.setdefault("bids", []).append(bid_details)
    return jsonify({"message": f"Bid submitted successfully by Supplier {supplier_id}"})

# Route: Analyze Bids
@app.route('/analyze_bids', methods=['GET'])
def analyze_bids():
    bids = session.get("bids", [])
    if not bids:
        return jsonify({"error": "No bids submitted for this event"}), 400

    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a procurement AI assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    analysis = eval(response['choices'][0]['message']['content'])
    """

    # Mock GPT-4 analysis response
    analysis = {
        "ranked_bids": [
            {"supplier_id": "S001", "rank": 1, "bid_amount": 15000, "delivery_time": 5},
            {"supplier_id": "S002", "rank": 2, "bid_amount": 15500, "delivery_time": 7}
        ],
        "anomalies": ["Supplier S003's bid amount is abnormally high."],
        "suggestions": ["Negotiate with Supplier S001 for better payment terms."]
    }

    return render_template("analyze_bids.html", analysis=analysis)

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
