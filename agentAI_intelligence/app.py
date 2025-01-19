from flask import Flask, request, jsonify, render_template, session
import pandas as pd
import openai  # Uncomment to enable OpenAI integration

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Uncomment and set your OpenAI API key
# openai.api_key = "your_openai_api_key"

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

    # Uncomment for OpenAI GPT-4 integration
    # """
    # prompt = f"""
    # You are an AI procurement assistant. Based on the following historical supplier data and buyer input, provide:
    # 1. Ranked supplier recommendations with match percentage and reasons.
    # 2. Risks associated with each supplier.
    # 3. AI insights including trends and optimizations.

    # Historical Supplier Data:
    # {historical_supplier_data}

    # Buyer Input:
    # {buyer_input}

    # Respond in JSON format:
    # {{
        # "ranked_suppliers": [
            # {{
                # "supplier_name": "Supplier Name",
                # "score": 95,
                # "match_percentage": 97,
                # "ranking_reason": "Explanation of ranking.",
                # "region": "Supplier region",
                # "risks": ["Risk 1", "Risk 2"],
                # "ai_insights": {{
                    # "trends": ["Trend 1", "Trend 2"],
                    # "optimizations": ["Optimization 1", "Optimization 2"]
                # }}
            # }},
            # ...
        # ],
        # "ai_insights": {{
            # "trends": [...],
            # "risks": [...],
            # "optimizations": [...]
        # }}
    # }}
    # """
    # try:
        # response = openai.ChatCompletion.create(
            # model="gpt-4",
            # messages=[{"role": "system", "content": "You are a procurement AI assistant."},
                      # {"role": "user", "content": prompt}]
        # )
        # output = eval(response['choices'][0]['message']['content'])
    # except Exception as e:
        # print(f"OpenAI GPT-4 Error: {e}")
        # return jsonify({"error": "Failed to get AI recommendations."}), 500
    # """

    # Mocked GPT-4 output
    output = {
        "ranked_suppliers": [
            {
                "supplier_name": "TechWorld",
                "score": 95,
                "match_percentage": 97,
                "ranking_reason": "Reliable and cost-effective.",
                "region": "North America",
                "risks": ["Occasional delays during peak seasons."],
                "ai_insights": {
                    "trends": ["Increased demand for electronics in North America."],
                    "optimizations": ["Negotiate long-term contracts for better pricing."]
                }
            },
            {
                "supplier_name": "DataMax",
                "score": 90,
                "match_percentage": 92,
                "ranking_reason": "Fast delivery and good pricing.",
                "region": "Europe",
                "risks": ["Slightly lower quality rating for certain items."],
                "ai_insights": {
                    "trends": ["European suppliers are offering discounts this quarter."],
                    "optimizations": ["Combine orders with other commodities to save costs."]
                }
            }
        ],
        "ai_insights": {
            "trends": [
                "RAM prices are expected to increase by 10% next quarter."
            ],
            "risks": [
                "Potential supply chain delays during peak seasons."
            ],
            "optimizations": [
                "Split orders across suppliers for better pricing and delivery times."
            ]
        }
    }

    session["supplier_recommendations"] = output
    return jsonify(output)

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

        # Prepare the buyer requirements
        buyer_requirements = session.get("event_data", {})

        # Uncomment for OpenAI GPT-4 integration
        
        # prompt = f"""
        # You are an AI procurement assistant. Based on the following supplier quotations and buyer requirements, provide:
        # 1. Ranked supplier quotes based on price, delivery time, quality, and additional terms.
        # 2. Explanations for the rankings, highlighting trade-offs.
        # 3. AI insights including trends, risks, and optimizations.

        # Buyer Requirements:
        # {buyer_requirements}

        # Supplier Quotations:
        # {supplier_quotations}

        # Respond in JSON format:
        # {{
            # "ranked_quotes": [
                # {{
                    # "supplier_name": "Supplier Name",
                    # "price_per_unit": 1200,
                    # "total_cost": 120000,
                    # "delivery_date": "2025-01-25",
                    # "additional_terms": "Free shipping for orders above $10,000.",
                    # "score": 96,
                    # "explanation": "Ranked high due to competitive pricing, fast delivery, and excellent terms."
                # }},
                # ...
            # ],
            # "ai_insights": {{
                # "trends": [...],
                # "risks": [...],
                # "optimizations": [...],
                # "sustainability": [...]
            # }}
        # }}
        
        # response = openai.ChatCompletion.create(
            # model="gpt-4",
            # messages=[{"role": "system", "content": "You are a procurement AI assistant."},
                      # {"role": "user", "content": prompt}]
        # )
        # output = eval(response['choices'][0]['message']['content'])
        
        
        # Mocked supplier data for testing
        quotes = [
            {
                "supplier_name": "TechWorld",
                "price_per_unit": 1200,
                "total_cost": 120000,
                "delivery_date": "2025-01-25",
                "additional_terms": "Free shipping for orders above $10,000.",
                "score": 96,
                "explanation": "Ranked high due to competitive pricing, fast delivery (2025-01-25), and excellent terms like free shipping."
            },
            {
                "supplier_name": "DataMax",
                "price_per_unit": 1150,
                "total_cost": 138000,
                "delivery_date": "2025-01-24",
                "additional_terms": "5% discount for orders above 150 units.",
                "score": 92,
                "explanation": "Strong ranking due to discounted pricing for bulk orders and early delivery (2025-01-24)."
            },
            {
                "supplier_name": "SupplyHub",
                "price_per_unit": 1180,
                "total_cost": 106200,
                "delivery_date": "2025-01-28",
                "additional_terms": "Includes free installation.",
                "score": 89,
                "explanation": "Good overall score due to moderate pricing and added benefit of free installation."
            },
            {
                "supplier_name": "CoreLink Solutions",
                "price_per_unit": 1250,
                "total_cost": 137500,
                "delivery_date": "2025-01-22",
                "additional_terms": "Priority delivery for urgent orders.",
                "score": 85,
                "explanation": "Ranked lower due to higher pricing despite fast delivery and priority handling."
            },
            {
                "supplier_name": "Global Components",
                "price_per_unit": 1100,
                "total_cost": 165000,
                "delivery_date": "2025-01-30",
                "additional_terms": "Free extended warranty for bulk orders over $150,000.",
                "score": 82,
                "explanation": "Lower ranking due to longer delivery times (2025-01-30) despite excellent bulk order terms."
            }
        ]
         
        # Example AI Insights (mocked)
        analysis = {
            "ranked_quotes": quotes,
            "ai_insights": {
                "trends": ["RAM prices are stable this quarter.", "High demand expected in Q2."],
                "risks": ["Potential delivery delays due to global chip shortages."],
                "optimizations": ["Negotiate bulk discounts with top suppliers.", "Split orders to minimize risks."],
                "sustainability": [
                    "TechWorld uses 100% recyclable packaging.",
                    "DataMax is ISO 14001 certified."
                ]
            }
        }

        return render_template('analyze_quotes.html', analysis=analysis, enumerate=enumerate)

    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
