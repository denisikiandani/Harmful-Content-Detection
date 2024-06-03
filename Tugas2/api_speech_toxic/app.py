import streamlit as st
import requests

# Fungsi untuk melakukan prediksi teks menggunakan Flask API
def predict_text(text):
    # Membuat request ke API
    url = 'http://localhost:8080/predict'
    payload = {'teks': text}
    response = requests.post(url, data=payload)
    return response.text

# Fungsi untuk melakukan prediksi audio menggunakan Flask API
def predict_audio(audio):
    # Membuat request ke API
    url = 'http://localhost:8080/predictaudio'
    files = {'audio': audio}
    response = requests.post(url, files=files)
    return response.text

# Fungsi untuk melakukan prediksi video menggunakan Flask API
def predict_video(video):
    # Membuat request ke API
    url = 'http://localhost:8080/predictvideo'
    files = {'video': video}
    response = requests.post(url, files=files)
    return response.text



# Fungsi utama aplikasi Streamlit
def main():
    st.title("Deteksi Threat dan Hate Speech")

    # Pilihan untuk memilih jenis input (teks, audio, atau video)
    option =  st.radio("Pilih jenis file:", ("Teks", "Audio", "Video"))

    if option == "Teks":
        # Mendapatkan input teks dari pengguna
        teks = st.text_area("Masukkan teks:")
        # Tombol untuk memprediksi teks
        if st.button("Prediksi Teks"):
            # Memanggil fungsi predict_text untuk melakukan prediksi
            output = predict_text(teks)
            # Menampilkan output prediksi
            st.text(output)
            

    elif option == "Audio":
        # Mendapatkan file audio dari pengguna
        audio_file = st.file_uploader("Unggah file audio:", type=["mp3"])
        if audio_file is not None:
            # Menampilkan file audio agar dapat diputar
            st.audio(audio_file, format='audio/mp3')
            # Tombol untuk memprediksi audio
            if st.button("Prediksi Audio"):
                # Memanggil fungsi predict_audio untuk melakukan prediksi
                output = predict_audio(audio_file)
                # Menampilkan output prediksi
                st.text(output)

    elif option == "Video":
        # Mendapatkan file video dari pengguna
        video_file = st.file_uploader("Unggah file video:", type=["mp4"])
        if video_file is not None:
            # Menampilkan file video agar dapat diputar
            st.video(video_file)
            # Tombol untuk memprediksi video
            if st.button("Prediksi Video"):
                # Memanggil fungsi predict_video untuk melakukan prediksi
                output = predict_video(video_file)
                # Menampilkan output prediksi
                st.text(output)
                
# Menjalankan aplikasi Streamlit
if __name__ == "__main__":
    main()
