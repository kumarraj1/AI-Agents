from flask import Flask, request, jsonify, render_template, session
import pandas as pd
import openai
import json

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

def chunk_data(data, chunk_size):
    """Divide large data into manageable chunks."""
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_suppliers', methods=['POST'])
def get_suppliers():
    buyer_input = request.json
    print(f"Buyer Input: {buyer_input}")

    chunk_size = 30  # Define the number of records per chunk
    all_ranked_suppliers = []
    all_ai_insights = {"trends": [], "risks": [], "optimizations": []}

    for chunk in chunk_data(historical_supplier_data, chunk_size):
        prompt = f"""
        You are an AI procurement assistant. Based on the following supplier data and buyer input, rank the suppliers and provide insights:

        Supplier Data:
        {chunk}

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
                    "explanation": "Detailed explanation for ranking.",
                    "region": "Supplier region",
                    "risks": ["Risk 1", "Risk 2"]
                }},
                ...
            ],
            "ai_insights": {{
                "trends": ["Trend 1", "Trend 2"],
                "risks": ["Risk 1", "Risk 2"],
                "optimizations": ["Optimization 1", "Optimization 2"]
            }}
        }}
        """

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a procurement AI assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            raw_output = response["choices"][0]["message"]["content"]
            json_output = eval(raw_output)

            # Append ranked suppliers
            all_ranked_suppliers.extend(json_output.get("ranked_suppliers", []))

            # Merge AI insights
            for key in all_ai_insights:
                all_ai_insights[key].extend(json_output.get("ai_insights", {}).get(key, []))

        except Exception as e:
            print(f"Error processing chunk: {e}")

    # Final sorting and ranking
    final_ranking = sorted(all_ranked_suppliers, key=lambda x: x["score"], reverse=True)

    # Deduplicate AI insights
    for key in all_ai_insights:
        all_ai_insights[key] = list(set(all_ai_insights[key]))

    return jsonify({
        "ranked_suppliers": final_ranking,
        "ai_insights": all_ai_insights
    })

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
            supplier_quotations = f.read().splitlines()

        buyer_requirements = session.get("event_data", {})

        # Define chunk size and initialize results
        chunk_size = 5  # Number of quotations per chunk
        all_ranked_quotes = []
        all_ai_insights = {"trends": [], "risks": [], "optimizations": [], "sustainability": []}

        for i in range(0, len(supplier_quotations), chunk_size):
            chunk = supplier_quotations[i:i + chunk_size]

            # Prepare OpenAI prompt for the current chunk
            prompt = f"""
            You are an AI procurement assistant. Based on the following supplier quotations and buyer requirements, provide:
            - Ranked supplier quotes with price, delivery time, and score.
            - Explanations for rankings.
            - AI insights including trends, risks, and optimizations.

            Buyer Requirements:
            {buyer_requirements}

            Supplier Quotations:
            {chunk}

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
                        "explanation": "Ranked high due to competitive pricing and fast delivery."
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
                messages=[
                    {"role": "system", "content": "You are a procurement AI assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            raw_output = response['choices'][0]['message']['content']
            json_output = eval(raw_output)

            # Append ranked quotes and merge AI insights
            all_ranked_quotes.extend(json_output.get("ranked_quotes", []))
            for key in all_ai_insights:
                all_ai_insights[key].extend(json_output.get("ai_insights", {}).get(key, []))

        # Deduplicate AI insights
        for key in all_ai_insights:
            all_ai_insights[key] = list(set(all_ai_insights[key]))

        # Final sorting of ranked quotes
        final_ranking = sorted(all_ranked_quotes, key=lambda x: x["score"], reverse=True)

        return render_template('analyze_quotes.html', analysis={
            "ranked_quotes": final_ranking,
            "ai_insights": all_ai_insights
        }, enumerate=enumerate)

    except Exception as e:
        print(f"OpenAI GPT-4 Error: {e}")
        return jsonify({"error": f"An error occurred: {e}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
