# Import library
import io
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS  # type: ignore
from werkzeug.utils import secure_filename
from handler import predict, predict_audio, predict_video, predict_text, transcribe_file_v2, generate_word_cloud


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
                # output = predict(teks)
                output = predict_text(teks)
                # Mengembalikan output
                return output
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
                output, full_transcript = predict_audio(audio)
                # Mengembalikan output dan transcript
                return jsonify({"output": output, "transcript": full_transcript})
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
                output, full_transcript = predict_video(video)
                # Mengembalikan output dan transcript
                return jsonify({"output": output, "transcript": full_transcript})
            except Exception as error:
                print(error)
                return jsonify({"status": "error"})
            
    @app.route('/generate-wordcloud', methods=['POST'])
    def generate_wordcloud_route():
        data = request.get_json()
        text = data['text']
        wordcloud_image = generate_word_cloud(text)

        if wordcloud_image:
            return send_file(
                io.BytesIO(wordcloud_image),
                mimetype='image/png',
                as_attachment=False,
                download_name='wordcloud.png'
            )
        else:
            return jsonify({"status": "error", "message": "Failed to generate word cloud."})

