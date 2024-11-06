from flask import Flask, request, render_template, jsonify
import pandas as pd
import re
import nltk

# Initialize Flask app
app = Flask(__name__)

# Download necessary NLTK resources
nltk.download('punkt')

# Load the dataset
try:
    df = pd.read_csv('olympics.csv')
    print("Dataset loaded successfully!")
except FileNotFoundError:
    print("Error: The file 'olympics.csv' was not found. Please check the file path.")

# Clean country names
df['Team/NOC'] = df['Team/NOC'].str.strip()  # Removing leading/trailing spaces

# Function to get total medals for a country
def get_total_medals(country_name):
    # Filter for the country in the dataset (case-insensitive)
    country_data = df[df['Team/NOC'].str.contains(country_name, case=False, na=False)]
    
    if country_data.empty:
        return "No data available for the specified country."
    
    gold_medals = country_data['Gold'].sum()
    silver_medals = country_data['Silver'].sum()
    bronze_medals = country_data['Bronze'].sum()
    total_medals = gold_medals + silver_medals + bronze_medals
    
    return gold_medals, silver_medals, bronze_medals, total_medals

# Parse user input to extract country
def parse_input(user_input):
    user_input = user_input.lower().strip()
    # Using regex to extract country name
    country_match = re.search(r'how many medals did ([\w\s]+) win', user_input)
    if country_match:
        return country_match.group(1)
    return None

# Route to serve the chatbot page
@app.route('/')
def home():
    return render_template('index.html')

# Route to handle chatbot messages (AJAX)
@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json['message']
    
    country_name = parse_input(user_input)
    
    if country_name:
        medals_data = get_total_medals(country_name)
        if isinstance(medals_data, str):
            return jsonify({"response": f"Bot: {medals_data}"})
        else:
            gold_medals, silver_medals, bronze_medals, total_medals = medals_data
            return jsonify({
                "response": f"Bot: {country_name.title()} won {gold_medals} gold, {silver_medals} silver, {bronze_medals} bronze, and {total_medals} total medals."
            })
    else:
        return jsonify({"response": "Bot: Sorry, I didn't understand that. Please ask me about medals, e.g., 'How many medals did USA win?'."})

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
