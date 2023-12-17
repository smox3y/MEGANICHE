from flask import Flask, request, jsonify
from videoScrape import scrape_tiktok_videos

app = Flask(__name__)

@app.route('/trigger', methods=['POST'])
def webhook():
    if request.method == 'POST':
        data = request.json
        print("Data received:", data)
        # Process the data here
        scrape_tiktok_videos(data)
        return jsonify({"status": "success", "message": "Data received"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
