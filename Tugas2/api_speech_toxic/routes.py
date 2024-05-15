# Import library
from flask import request, jsonify  #
from handler import predict, predict_audio, predict_video


# Function setupRoutes:
# Untuk mendeklarasi endpoint dari API kita
def setup_routes(app):
    # Endpoint /predict:
    # Untuk deteksi threat dan hate speech pada teks
    @app.route('/predict', methods=['POST'])
    def route_predict():
        if request.method == 'POST':
            try:
                # Mengambil teks dari request
                teks = request.form.get('teks')
                # Memproses teks
                output = predict(teks)
                # Mengembalikan output
                return jsonify(output)
            except Exception as error:
                print(error)
                return jsonify({"status": "error"})

    # Endpoint /predictaudio:
    # Untuk deteksi threat dan hate speech pada audio
    @app.route('/predictaudio', methods=['POST'])
    def route_predictaudio():
        if request.method == 'POST':
            try:
                # Mengambil audio dari request
                audio = request.files.get('audio')
                # Memproses audio
                output = predict_audio(audio)
                # Mengembalikan output
                return jsonify(output)
            except Exception as error:
                print(error)
                return jsonify({"status": "error"})

    # Endpoint /predictvideo:
    # Untuk deteksi threat dan hate speech pada video
    @app.route('/predictvideo', methods=['POST'])
    def route_predictvideo():
        if request.method == 'POST':
            try:
                # Mengambil video dari request
                video = request.files.get('video')
                # Memproses video
                output = predict_video(video)
                # Mengembalikan output
                return jsonify(output)
            except Exception as error:
                print(error)
                return jsonify({"status": "error"})
