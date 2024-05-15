# Import Library
import io
import json
import os
import tensorflow as tf
import numpy as np
import pandas as pd
from tensorflow.keras.layers import TextVectorization  # tokenization|
import pickle

# Import Library
from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech
from google.oauth2 import service_account
from moviepy.editor import VideoFileClip

# Load Model
model = tf.keras.models.load_model('../load_model_integration/toxic-v1.h5')

# Lables Predict
labels = ['toxic', 'severe_toxic', 'obscene', 'threat', 'insult', 'identity_hate']
# toxic == toxic
# sever_toxic == toxic_parah
# obscene == cabul
# threat == ancaman
# insult == menyinggung
# indentity_hate == benci personal

# Import Vectorizer
with open('vectorizer_config.pkl', 'rb') as f:
    vectorizer_config = pickle.load(f)
with open('vectorizer_vocab.pkl', 'rb') as f:
    vectorizer_vocab = pickle.load(f)

# Set Vectorizer
vectorizer = TextVectorization.from_config(vectorizer_config)
vectorizer.set_vocabulary(vectorizer_vocab)


# Function transkrip audio Synchronous
# Limitasi Synchronous:
# ---------------------------------
# Audio Maximum 1 Menit
# Audio Maximum 10 MB
# ---------------------------------
def transcribe_file_v2(project_id: str, audio_file: str) -> cloud_speech.RecognizeResponse:
    # Instantiates client
    credentials = service_account.Credentials.from_service_account_file('gcloud_apikey.json')
    client = SpeechClient(credentials=credentials)
    # Baca file dalam bytes
    with open(audio_file, "rb") as f:
        content = f.read()
    # Config untuk speech recognition
    config = cloud_speech.RecognitionConfig(
        auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
        language_codes=["en-US"],
        model="long",
    )
    # Membentuk objek request
    request = cloud_speech.RecognizeRequest(
        recognizer=f"projects/{project_id}/locations/global/recognizers/_",
        config=config,
        content=content,
    )
    # Transkrip audio menjadi teks
    response = client.recognize(request=request)
    # Return respon transkrip
    return response


# Function convert video ke audio
def convert_mp3(video_path):
    # Load video
    video_clip = VideoFileClip(video_path)
    audio_clip = video_clip.audio
    audio_clip.write_audiofile("audio.mp3")


# Function predict threat dan hate pada teks
def predict(teks):
    # Input data teks
    input_data = teks
    # Membuat vektor setiap teks masukan dalam daftar
    vectorized_texts = [vectorizer(text) for text in input_data]
    # Pad urutan dengan panjang yang sama
    padded_texts = tf.keras.preprocessing.sequence.pad_sequences(vectorized_texts, maxlen=1800)
    # Melakukan prediksi
    predictions = model.predict(padded_texts)
    binary_predictions = (predictions > 0.5).astype(int)
    # Membuat buffer untuk menyimpan output
    output_buffer = io.StringIO()
    label_index = {label: [] for label in labels}
    total_predictions = binary_predictions.sum(axis=0)
    for i, (prediction, text) in enumerate(zip(binary_predictions, input_data)):
        # Menulis ke buffer alih-alih mencetak langsung
        for j, (label, pred) in enumerate(zip(labels, prediction)):
            if pred == 1:
                output_buffer.write(f"Text: {text}\n")
                output_buffer.write(f"Prediction: {label} Value: {predictions[i][j]}\n")
                label_index[label].append(i)  # Menyimpan indeks di mana label diprediksi sebagai 1
        output_buffer.write("\n")
    for label, total in zip(labels, total_predictions):
        output_buffer.write(f"Total {label} predictions: {total}\n")
        output_buffer.write(f"Index Kalimat yang terdeteksi {label}: {label_index[label]}\n")
        output_buffer.write("\n")
    # Mendapatkan semua output sebagai string
    output_string = output_buffer.getvalue()
    # Jangan lupa untuk menutup buffer setelah selesai
    output_buffer.close()
    return output_string


# Function predict threat dan hate pada video
def predict_video(video):
    # Menyimpan video
    video.save("video.mp4")
    # Convert video ke audio
    convert_mp3("video.mp4")
    # Transkrip audio dengan Google Speech API
    transkrip = transcribe_file_v2(project_id="data-science-programming-ti24", audio_file="audio.mp3")
    # Menyimpan hasil transkrip ke bentuk List
    list_hasil_transkrip = list()
    for hasil in transkrip.results:
        teks = f'{hasil.alternatives[0].transcript}'
        list_hasil_transkrip.append(teks)
    # Prediksi threat dan hate speech
    output = predict(list_hasil_transkrip)
    # Menghapus file video dan audio setelah prediksi
    files_remove = ['audio.mp3', 'video.mp4']
    for file_name in files_remove:
        if os.path.exists(file_name):
            os.remove(file_name)
        else:
            pass
    # Return
    return output


# Function predict threat dan hate pada audio
def predict_audio(audio):
    # Menyimpan audio
    audio.save("audio.mp3")
    # Transkrip audio dengan Google Speech API
    transkrip = transcribe_file_v2(project_id="data-science-programming-ti24", audio_file="audio.mp3")
    # Menyimpan hasil transkrip ke bentuk List
    list_hasil_transkrip = list()
    for hasil in transkrip.results:
        teks = f'{hasil.alternatives[0].transcript}'
        list_hasil_transkrip.append(teks)
    # Prediksi threat dan hate speech
    output = predict(list_hasil_transkrip)
    # Menghapus file video dan audio setelah prediksi
    files_remove = ['audio.mp3', 'video.mp4']
    for file_name in files_remove:
        if os.path.exists(file_name):
            os.remove(file_name)
        else:
            pass
    # Return
    return output
