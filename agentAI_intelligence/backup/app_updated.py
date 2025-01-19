from flask import Flask, request, jsonify, render_template, session
import pandas as pd
import openai

app = Flask(__name__)
app.secret_key = "supersecretkey"

# OpenAI API Key
openai.api_key = "your_openai_api_key"

# Load historical supplier data
try:
    historical_supplier_data = pd.read_csv("data/historical_supplier_data.csv").to_dict(orient="records")
    print(f"Loaded {len(historical_supplier_data)} historical supplier records.")
except Exception as e:
    print(f"Error loading supplier data: {e}")
    historical_supplier_data = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_suppliers', methods=['POST'])
def get_suppliers():
    buyer_input = request.json
    print(f"Buyer Input: {buyer_input}")

    try:
        # Prepare OpenAI prompt
        prompt = f"""
        You are an AI procurement assistant. Based on the following historical supplier data and buyer input, provide:
        1. Ranked supplier recommendations with match percentage, scores, and reasons.
        2. Explanations for each ranking, including trade-offs and strengths.
        3. Risks associated with each supplier.
        4. AI insights, including trends and optimizations.

        Historical Supplier Data:
        {historical_supplier_data}

        Buyer Input:
        {buyer_input}

        Respond in JSON format:
        {{
            "ranked_suppliers": [
                {{
                    "supplier_name": "Supplier Name",
                    "score": 95,
                    "match_percentage": 97,
                    "ranking_reason": "Reason for ranking.",
                    "explanation": "Detailed explanation for why this supplier is ranked high or low.",
                    "region": "Supplier region",
                    "risks": ["Risk 1", "Risk 2"],
                    "ai_insights": {{
                        "trends": ["Trend 1", "Trend 2"],
                        "optimizations": ["Optimization 1", "Optimization 2"]
                    }}
                }},
                ...
            ],
            "ai_insights": {{
                "trends": [...],
                "risks": [...],
                "optimizations": [...]
            }}
        }}
        """
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "You are a procurement AI assistant."},
                      {"role": "user", "content": prompt}]
        )
        output = eval(response['choices'][0]['message']['content'])

        # Store recommendations in session
        session["supplier_recommendations"] = output
        return jsonify(output)

    except Exception as e:
        print(f"OpenAI GPT-4 Error: {e}")
        return jsonify({"error": "Failed to get AI recommendations."}), 500

@app.route('/edit_event', methods=['GET', 'POST'])
def edit_event():
    if request.method == 'POST':
        selected_suppliers = request.json.get("selected_suppliers", [])
        print(f"Selected Suppliers: {selected_suppliers}")
        session["selected_suppliers"] = selected_suppliers
        return jsonify({"message": "Suppliers selected successfully!"})
    
    return render_template('edit_event.html', selected_suppliers=session.get("selected_suppliers", []))

@app.route('/publish_event', methods=['POST'])
def publish_event():
    event_data = request.json
    print(f"Published Event Data: {event_data}")
    session["event_data"] = event_data
    return jsonify({"message": "Event published successfully!"})

@app.route('/analyze_quotes', methods=['GET'])
def analyze_quotes():
    try:
        # Read supplier quotations from a file
        with open('supplier_quotations.txt', 'r') as f:
            supplier_quotations = f.read()

        # Prepare buyer requirements
        buyer_requirements = session.get("event_data", {})

        # Prepare OpenAI prompt
        prompt = f"""
        You are an AI procurement assistant. Based on the following supplier quotations and buyer requirements, provide:
        1. Ranked supplier quotes based on price, delivery time, quality, and additional terms.
        2. Explanations for the rankings, highlighting trade-offs.
        3. AI insights including trends, risks, and optimizations.

        Buyer Requirements:
        {buyer_requirements}

        Supplier Quotations:
        {supplier_quotations}

        Respond in JSON format:
        {{
            "ranked_quotes": [
                {{
                    "supplier_name": "Supplier Name",
                    "price_per_unit": 1200,
                    "total_cost": 120000,
                    "delivery_date": "2025-01-25",
                    "additional_terms": "Free shipping for orders above $10,000.",
                    "score": 96,
                    "explanation": "Ranked high due to competitive pricing, fast delivery, and excellent terms."
                }},
                ...
            ],
            "ai_insights": {{
                "trends": [...],
                "risks": [...],
                "optimizations": [...],
                "sustainability": [...]
            }}
        }}
        """
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "You are a procurement AI assistant."},
                      {"role": "user", "content": prompt}]
        )
        output = eval(response['choices'][0]['message']['content'])

        # Render the AI analysis
        return render_template('analyze_quotes.html', analysis=output, enumerate=enumerate)

    except Exception as e:
        print(f"OpenAI GPT-4 Error: {e}")
        return jsonify({"error": f"An error occurred: {e}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
