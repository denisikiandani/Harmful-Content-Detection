# Import Library
import os
import io
import json
import pickle
import numpy as np
import pandas as pd

import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

from wordcloud import WordCloud
import matplotlib.pyplot as plt

import tensorflow as tf
from tensorflow.keras.layers import TextVectorization # type: ignore #tokenization|
import ast

# Import Library
from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech
from google.oauth2 import service_account
from moviepy.editor import VideoFileClip

# Load Model
model = tf.keras.models.load_model('../model_data/toxic-v2.h5')

# Lables Predict
labels = ['toxic', 'sangat_toxic', 'cabul', 'ancaman', 'penghinaan', 'rasis']
# toxic == toxic
# sever_toxic == toxic_parah
# obscene == cabul
# threat == ancaman
# insult == penghinaan 
# indentity_hate == rasis/benci personal(gender, ras, etnis, agama, orientasi seksual, dll)

# Import Vectorizer
with open('../model_data/vectorizer_config_v2.pkl', 'rb') as f:
    vectorizer_config = pickle.load(f)
with open('../model_data/vectorizer_vocab_v2.pkl', 'rb') as f:
    vectorizer_vocab = pickle.load(f)

# Inisialisasi stopwords dan lemmatizer
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

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
    audio_clip.close()
    video_clip.close()



# Function untuk menampilkan wordcloud
def plot_cloud(wordcloud):
    plt.figure(figsize=[10, 8])
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.show()

def generate_word_cloud(text):
    wordcloud = WordCloud(width = 800, height = 800, 
                background_color ='white', 
                stopwords = stop_words, 
                min_font_size = 10).generate(text)
    return wordcloud.to_image()

def normalize_text(text):
    text = text.lower()  # Ubah menjadi huruf kecil
    text = re.sub(r"i'm", "i am", text)
    text = re.sub(r"don't", "do not", text)
    text = re.sub(r"can't", "cannot", text)
    text = re.sub(r"won't", "will not", text)
    text = re.sub(r"it's", "it is", text)
    text = re.sub(r"that's", "that is", text)
    text = re.sub(r"there's", "there is", text)
    text = re.sub(r"what's", "what is", text)
    text = re.sub(r"who's", "who is", text)
    text = re.sub(r"isn't", "is not", text)
    text = re.sub(r"wasn't", "was not", text)
    text = re.sub(r"weren't", "were not", text)
    text = re.sub(r"didn't", "did not", text)
    text = re.sub(r"haven't", "have not", text)
    text = re.sub(r"hasn't", "has not", text)
    text = re.sub(r"shouldn't", "should not", text)
    text = re.sub(r"couldn't", "could not", text)
    text = re.sub(r"wouldn't", "would not", text)
    text = re.sub(r"ain't", "are not", text)
    text = re.sub(r"ive", "i have", text)
    text = re.sub(r"ok", "okay", text)
    text = re.sub(r"they're", "they are", text)
    return text

def clean_text(text):
    text = re.sub(r'@[A-Za-z0-9_]+','',text) # Hapus mention
    text = re.sub(r'#\w+','',text) # Hapus hashtag
    text = re.sub(r'RT[\s]+','',text) # Hapus retweet
    text = re.sub(r'https?://\S+','',text) # Hapus url
    text = re.sub(r'\r\n', ' ', text)  # Mengubah \r\n menjadi spasi
    text = re.sub(r'\r|\n', ' ', text) # Hapus karakter escape seperti \r dan \n
    text = re.sub(r'[^A-Za-z0-9 ]','',text) # Hapus karakter non alpha numeric
    text = re.sub(r'\d+', '', text) # hapus angka
    text = re.sub(r'\s+',' ',text).strip() # Hapus spasi berlebih

    return text

def preprocess_text(text):
    text = normalize_text(text)  # Normalisasi teks
    text = clean_text(text)  # Bersihkan teks
    
    # stopwords dan lemmatize
    text = ' '.join([lemmatizer.lemmatize(word) for word in text.split() if word not in stop_words])
    return text


# Function predict threat dan hate pada teks
def predict(teks):
    # Jika masih dalam bentuk String
    if type(teks) == str:
        # Input data teks
        input_data = ast.literal_eval(teks)
    # Jika sudah dalam bentuk List
    else:
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


# Function predict threat dan hate pada teks
def predict_text(teks):
    input_data = teks
    clean_input = preprocess_text(input_data)
    
    # Membuat vektor setiap teks masukan dalam daftar
    vectorized_texts = vectorizer([clean_input])
    # # Pad sequence dengan panjang yg sa,a
    padded_texts = tf.keras.preprocessing.sequence.pad_sequences(vectorized_texts, maxlen=1800)
    # Melakukan prediksi
    predictions = model.predict(padded_texts)
    binary_predictions = (predictions > 0.5).astype(int)
    # Membuat buffer untuk menyimpan output
    output_buffer = io.StringIO()
    
    # Menampilkan teks input
    output_buffer.write("Teks Input:\n")
    output_buffer.write(f"{input_data}\n\n")

    # Menampilkan hasil prediksi untuk setiap label yang bernilai 1
    for i, (label, prediction_value) in enumerate(zip(labels, predictions[0])):
        binary_value = binary_predictions[0][i]
        if binary_value == 1:
            output_buffer.write(f"Label: {label}\n")
            output_buffer.write(f"Akurasi Prediksi: {prediction_value}\n")
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
