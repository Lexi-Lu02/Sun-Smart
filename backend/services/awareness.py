from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 允许前端跨域访问


@app.route("/")
def home():
    return jsonify({
        "message": "SunSmart Awareness API is running."
    })


@app.route("/api/awareness/skin-cancer", methods=["GET"])
def get_skin_cancer_data():
    """
    返回皮肤癌影响图表数据
    前端对应:
    - labels
    - values
    - datasetLabel
    """
    data = {
        "labels": ["15-24", "25-34", "35-44", "45-54", "55+"],
        "values": [1200, 2400, 3900, 5200, 6800],
        "datasetLabel": "Estimated Cases"
    }
    return jsonify(data)


@app.route("/api/awareness/heat-trend", methods=["GET"])
def get_heat_trend_data():
    """
    返回热趋势图表数据
    前端对应:
    - labels
    - values
    - datasetLabel
    """
    data = {
        "labels": ["2019", "2020", "2021", "2022", "2023", "2024"],
        "values": [29.1, 29.4, 29.8, 30.2, 30.5, 31.0],
        "datasetLabel": "Average Summer Temperature (°C)"
    }
    return jsonify(data)


@app.route("/api/awareness/content", methods=["GET"])
def get_awareness_content():
    """
    返回 myths / facts / takeaway
    """
    data = {
        "myths": [
            {
                "title": "Cloudy days are safe.",
                "description": "UV radiation can still reach your skin even when the sky looks overcast."
            },
            {
                "title": "Only hot weather causes skin damage.",
                "description": "Heat and UV are different. A cool day can still have dangerous UV levels."
            },
            {
                "title": "Young people do not need daily protection.",
                "description": "UV damage builds over time, so protective habits should start early."
            }
        ],
        "facts": [
            "Skin damage can happen without immediate pain or visible redness.",
            "Australia’s UV index is often high enough to require protection for much of the year.",
            "Visual awareness helps people understand risk better than simple warnings alone."
        ],
        "takeaway": (
            "By seeing the trends visually, users are more likely to treat sun protection "
            "as a regular habit rather than an occasional action."
        )
    }
    return jsonify(data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)