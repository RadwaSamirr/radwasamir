from flask import Flask, jsonify, request, render_template
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
CORS(app)

# Configurations
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define model
class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wins = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    ties = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {'wins': self.wins, 'losses': self.losses, 'ties': self.ties}

# Swagger config
API_URL = '/static/openapi.yaml'
SWAGGER_URL = '/api/docs'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "RPS"}
)
app.register_blueprint(swaggerui_blueprint)

# Routes
@app.route("/")
def index():
    score_data = Score.query.first()
    if score_data:
        return render_template('index.html', score=score_data.to_dict())
    return render_template('index.html', score={'wins': 0, 'losses': 0, 'ties': 0})

@app.route("/score", methods=['GET'])
def get_score():
    score_data = Score.query.first()
    if score_data:
        return jsonify(score_data.to_dict())
    return jsonify({"wins": 0, "losses": 0, "ties": 0}), 404

@app.route("/score", methods=['PUT'])
def set_score():
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
    if component not in ['wins', 'losses', 'ties']:
        return jsonify({"error": "Invalid component"}), 400

    score_data = Score.query.first()
    if score_data:
        setattr(score_data, component, 0)
        db.session.commit()
        return '', 204
    return jsonify({"message": "No score data found"}), 404

@app.route("/health-check")
def health_check():
    return 'snafu: situation normal all fired up!'

# Run app
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)

# ----------- TESTS SECTION (included in same file) -----------
def run_tests():
    import pytest

    @pytest.fixture
    def client():
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        with app.test_client() as client:
            with app.app_context():
                db.create_all()
            yield client

    def test_health_check(client):
        res = client.get('/health-check')
        assert res.status_code == 200
        assert b'snafu' in res.data

    def test_get_score_empty(client):
        res = client.get('/score')
        assert res.status_code == 404

# To run: `pytest app.py`
