# Import library
import io
from flask import request, jsonify  #
from handler import predict, predict_audio, predict_video, predict_text, generate_wordcloud, transcribe_file_v2


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
                output = predict_audio(audio)
                # Mengembalikan output
                return output
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
                return output
            except Exception as error:
                print(error)
                return jsonify({"status": "error"})

    @app.route('/wordcloud', methods=['POST'])
    def route_wordcloud():
        if request.method == 'POST':
            try:
                if 'teks' in request.form:
                    teks = request.form.get('teks')
                    # Generate WordCloud dari teks
                    wordcloud_image = generate_wordcloud(teks)
                    # Convert gambar menjadi byte array
                    img_byte_arr = io.BytesIO()
                    wordcloud_image.save(img_byte_arr, format='PNG')
                    img_byte_arr = img_byte_arr.getvalue()
                    # Mengembalikan byte array gambar
                    return img_byte_arr
                elif 'audio' in request.files:
                    audio_file = request.files.get('audio')
                    # Transkrip audio menggunakan Google Speech API
                    transkrip = transcribe_file_v2(audio_file)
                    # Generate WordCloud dari transkrip audio
                    wordcloud_image = generate_wordcloud(transkrip)
                    img_byte_arr = io.BytesIO()
                    wordcloud_image.save(img_byte_arr, format='PNG')
                    img_byte_arr = img_byte_arr.getvalue()
                    return img_byte_arr
                elif 'video' in request.files:
                    video_file = request.files.get('video')
                    # Transkrip video menggunakan Google Speech API
                    transkrip = transcribe_file_v2(video_file)
                    # Generate WordCloud dari transkrip video
                    wordcloud_image = generate_wordcloud(transkrip)
                    img_byte_arr = io.BytesIO()
                    wordcloud_image.save(img_byte_arr, format='PNG')
                    img_byte_arr = img_byte_arr.getvalue()
                    return img_byte_arr
                else:
                    return jsonify({"status": "error", "message": "Invalid request format"})
            except Exception as error:
                print(error)
                return jsonify({"status": "error", "message": str(error)})