import streamlit as st
import requests
from PIL import Image
import io

import queue
import re
import sys
import time
from google.oauth2 import service_account

from google.cloud import speech
import pyaudio

# Import the predict_text function from handler.py
from handler import predict_text

# Function to predict text using Flask API
def predict_text(text):
    url = 'http://localhost:8080/predict'
    payload = {'teks': text}
    response = requests.post(url, data=payload)
    return response.text

# Function to predict audio using Flask API
def predict_audio(audio):
    url = 'http://localhost:8080/predictaudio'
    files = {'audio': audio}
    response = requests.post(url, files=files)
    return response.json()

# Function to predict video using Flask API
def predict_video(video):
    url = 'http://localhost:8080/predictvideo'
    files = {'video': video}
    response = requests.post(url, files=files)
    return response.json()

# Function to generate word cloud using Flask API
def generate_word_cloud(text):
    url = 'http://localhost:8080/generate-wordcloud'
    response = requests.post(url, json={'text': text})
    if response.status_code == 200:
        image = Image.open(io.BytesIO(response.content))
        return image
    else:
        st.error(f"Failed to generate word cloud. Status code: {response.status_code}")
        st.error(f"Response: {response.json()}")
        return None

def handle_realtime(transcript_placeholder, predictions_placeholder):
    STREAMING_LIMIT = 240000  # 4 minutes
    SAMPLE_RATE = 16000
    CHUNK_SIZE = int(SAMPLE_RATE / 10)  # 100ms

    def get_current_time() -> int:
        """Return Current Time in MS."""
        return int(round(time.time() * 1000))

    class ResumableMicrophoneStream:
        """Opens a recording stream as a generator yielding the audio chunks."""

        def __init__(self, rate, chunk_size) -> None:
            self._rate = rate
            self.chunk_size = chunk_size
            self._num_channels = 1
            self._buff = queue.Queue()
            self.closed = True
            self.start_time = get_current_time()
            self.restart_counter = 0
            self.audio_input = []
            self.last_audio_input = []
            self.result_end_time = 0
            self.is_final_end_time = 0
            self.final_request_end_time = 0
            self.bridging_offset = 0
            self.last_transcript_was_final = False
            self.new_stream = True
            self._audio_interface = pyaudio.PyAudio()
            self._audio_stream = self._audio_interface.open(
                format=pyaudio.paInt16,
                channels=self._num_channels,
                rate=self._rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._fill_buffer,
            )

        def __enter__(self) -> object:
            self.closed = False
            return self

        def __exit__(self, type, value, traceback) -> object:
            self._audio_stream.stop_stream()
            self._audio_stream.close()
            self.closed = True
            self._buff.put(None)
            self._audio_interface.terminate()

        def _fill_buffer(self, in_data, *args, **kwargs) -> object:
            self._buff.put(in_data)
            return None, pyaudio.paContinue

        def generator(self):
            while not self.closed:
                data = []

                if self.new_stream and self.last_audio_input:
                    chunk_time = STREAMING_LIMIT / len(self.last_audio_input)

                    if chunk_time != 0:
                        if self.bridging_offset < 0:
                            self.bridging_offset = 0

                        if self.bridging_offset > self.final_request_end_time:
                            self.bridging_offset = self.final_request_end_time

                        chunks_from_ms = round(
                            (self.final_request_end_time - self.bridging_offset)
                            / chunk_time
                        )

                        self.bridging_offset = round(
                            (len(self.last_audio_input) - chunks_from_ms) * chunk_time
                        )

                        for i in range(chunks_from_ms, len(self.last_audio_input)):
                            data.append(self.last_audio_input[i])

                    self.new_stream = False

                chunk = self._buff.get()
                self.audio_input.append(chunk)

                if chunk is None:
                    return
                data.append(chunk)
                while True:
                    try:
                        chunk = self._buff.get(block=False)

                        if chunk is None:
                            return
                        data.append(chunk)
                        self.audio_input.append(chunk)

                    except queue.Empty:
                        break

                yield b"".join(data)

    def listen_print_loop(responses, stream, transcript_list, predictions_list):
        for response in responses:
            if get_current_time() - stream.start_time > STREAMING_LIMIT:
                stream.start_time = get_current_time()
                break

            if not response.results:
                continue

            result = response.results[0]

            if not result.alternatives:
                continue

            transcript = result.alternatives[0].transcript

            result_seconds = 0
            result_micros = 0

            if result.result_end_time.seconds:
                result_seconds = result.result_end_time.seconds

            if result.result_end_time.microseconds:
                result_micros = result.result_end_time.microseconds

            stream.result_end_time = int((result_seconds * 1000) + (result_micros / 1000))

            corrected_time = (
                stream.result_end_time
                - stream.bridging_offset
                + (STREAMING_LIMIT * stream.restart_counter)
            )

            if result.is_final:
                transcript_list.append(transcript)
                predictions = predict_text(transcript)
                predictions_list.append(predictions)

                transcript_placeholder.text("\n".join(transcript_list))
                predictions_placeholder.text("\n".join(predictions_list))

                stream.is_final_end_time = stream.result_end_time
                stream.last_transcript_was_final = True

                if re.search(r"\b(exit|quit)\b", transcript, re.I):
                    stream.closed = True
                    break
            else:
                transcript_placeholder.text("\n".join(transcript_list + [transcript]))
                stream.last_transcript_was_final = False

    def main():
        credentials = service_account.Credentials.from_service_account_file('gcloud_apikey.json')
        client = speech.SpeechClient(credentials=credentials)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=SAMPLE_RATE,
            language_code="en-US",
        )

        streaming_config = speech.StreamingRecognitionConfig(
            config=config,
            interim_results=True,
        )

        transcript_list = []
        predictions_list = []

        with ResumableMicrophoneStream(SAMPLE_RATE, CHUNK_SIZE) as stream:
            while not stream.closed:
                stream.audio_input = []
                audio_generator = stream.generator()

                requests = (
                    speech.StreamingRecognizeRequest(audio_content=content)
                    for content in audio_generator
                )

                responses = client.streaming_recognize(
                    config=streaming_config,
                    requests=requests
                )

                listen_print_loop(responses, stream, transcript_list, predictions_list)

    main()

# Main Streamlit app function
def main():
    st.title("Sistem Pendeteksi Konten Berbahaya secara Otomatis")
    st.write("Label Deteksi: Toxic, Sangat Toxic, Cabul, Ancaman, Rasis")
    # Choose input type
    option = st.radio("Pilih jenis file:", ("Teks", "Audio", "Video", "Realtime"))

    if option == "Teks":
        teks = st.text_area("Masukkan teks:")
        if st.button("Prediksi Teks"):
            st.header("Hasil Deteksi Text")
            output = predict_text(teks)
            st.text(output)
            
            st.header("Word Cloud")
            wordcloud_image = generate_word_cloud(teks)
            if wordcloud_image:
                st.image(wordcloud_image)
            else:
                st.write("Failed to generate word cloud.")

    elif option == "Audio":
        audio_file = st.file_uploader("Unggah file audio:", type=["mp3"])
        if audio_file is not None:
            st.audio(audio_file, format='audio/mp3')
            if st.button("Prediksi Audio"):
                st.header("Hasil Deteksi Audio")
                response = predict_audio(audio_file)
                output = response['output']
                transcript = response['transcript']
                st.text(output)
                
                st.header("Word Cloud")
                wordcloud_image = generate_word_cloud(transcript)
                if wordcloud_image:
                    st.image(wordcloud_image)
                else:
                    st.write("Failed to generate word cloud.")

    elif option == "Video":
        video_file = st.file_uploader("Unggah file video:", type=["mp4"])
        if video_file is not None:
            st.video(video_file)
            if st.button("Prediksi Video"):
                st.header("Hasil Deteksi Konten Video")
                response = predict_video(video_file)
                output = response['output']
                transcript = response['transcript']
                st.text(output)
                
                st.header("Word Cloud")
                wordcloud_image = generate_word_cloud(transcript)
                if wordcloud_image:
                    st.image(wordcloud_image)
                else:
                    st.write("Failed to generate word cloud.")
                    
    elif option == "Realtime":
        if st.button("Mulai Realtime Detection"):
            st.header("Hasil Deteksi Realtime")
            transcript_placeholder = st.empty()
            predictions_placeholder = st.empty()
            handle_realtime(transcript_placeholder, predictions_placeholder)

if __name__ == "__main__":
    main()
