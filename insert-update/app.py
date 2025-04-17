from flask import Flask, jsonify, request, render_template
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
CORS(app)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the Score Model
class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wins = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    ties = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {'wins': self.wins, 'losses': self.losses, 'ties': self.ties}

API_URL = '/static/openapi.yaml'
SWAGGER_URL = '/api/docs'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "RPS"
    },
)
app.register_blueprint(swaggerui_blueprint)

@app.route("/", methods=['GET'])
def index():
    """Renders the score HTML page."""
    score_data = Score.query.first()
    if score_data:
        return render_template('index.html', score=score_data.to_dict())
    return render_template('index.html', score={'wins': 0, 'losses': 0, 'ties': 0})

@app.route("/score", methods=['GET'])
def get_score():
    """Get the current score from the database (for API requests)."""
    score_data = Score.query.first()
    if score_data:
        return jsonify(score_data.to_dict())
    return jsonify({"wins": 0, "losses": 0, "ties": 0}), 404

@app.route("/score", methods=['PUT'])
def set_score():
    """Set a new score in the database (from HTML form)."""
    data = request.get_json()
    score_data = Score.query.first()
    if score_data:
        score_data.wins = data.get('wins', score_data.wins)
        score_data.losses = data.get('losses', score_data.losses)
        score_data.ties = data.get('ties', score_data.ties)
    else:
        new_score = Score(wins=data.get('wins', 0), losses=data.get('losses', 0), ties=data.get('ties', 0))
        db.session.add(new_score)
    db.session.commit()
    return jsonify(Score.query.first().to_dict()), 200

@app.route("/score/<component>", methods=['DELETE'])
def delete_score_component(component):
    """Resets a specific score component to zero."""
    if component not in ['wins', 'losses', 'ties']:
        return jsonify({"error": "Invalid component"}), 400

    score_data = Score.query.first()
    if score_data:
        setattr(score_data, component, 0)
        db.session.commit()
        return '', 204
    else:
        return jsonify({"message": "No score data found"}), 404

@app.route('/health-check')
def health_check():
    return 'snafu: situation normal all fired up!'

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
