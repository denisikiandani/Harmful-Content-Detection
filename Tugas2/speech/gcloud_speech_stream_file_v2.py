# Import Library
from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech as cloud_speech_types
from google.oauth2 import service_account


def transcribe_streaming_v2(project_id, api_key, audio_file):

    # Instantiates a client
    credentials = service_account.Credentials.from_service_account_file(api_key)
    client = SpeechClient(credentials=credentials)

    # Reads a file as bytes
    with open(audio_file, "rb") as f:
        content = f.read()

    sample_rate = 16000  # Misalkan sample rate adalah 16000 Hz (16kHz)
    desired_duration = 1  # Durasi yang diinginkan untuk setiap chunk dalam detik

    # In practice, stream should be a generator yielding chunks of audio data
    # chunk_length = len(content) // 1000
    chunk_length = sample_rate * desired_duration
    stream = [
        content[start: start + chunk_length]
        for start in range(0, len(content), chunk_length)
    ]
    audio_requests = (
        cloud_speech_types.StreamingRecognizeRequest(audio=audio) for audio in stream
    )

    recognition_config = cloud_speech_types.RecognitionConfig(
        auto_decoding_config=cloud_speech_types.AutoDetectDecodingConfig(),
        language_codes=["en-US"],
        model="long",
    )
    streaming_config = cloud_speech_types.StreamingRecognitionConfig(
        config=recognition_config
    )
    config_request = cloud_speech_types.StreamingRecognizeRequest(
        recognizer=f"projects/{project_id}/locations/global/recognizers/_",
        streaming_config=streaming_config,
    )

    def requests(config: cloud_speech_types.RecognitionConfig, audio: list) -> list:
        yield config
        yield from audio

    # Transcribes the audio into text
    responses_iterator = client.streaming_recognize(
        requests=requests(config_request, audio_requests)
    )

    responses = []
    list_transkrip = []

    for response in responses_iterator:
        responses.append(response)
        for result in response.results:
            list_sementara = [result.alternatives[0].transcript,
                              result.alternatives[0].confidence,
                              result.result_end_offset.seconds]
            list_transkrip.append(list_sementara)
            print(f"Transcript: {str(result.alternatives[0].transcript)}")
            print(f"Confidence: {str(result.alternatives[0].confidence)}")
            print(f"Seconds: {str(result.result_end_offset.seconds)}")
            print("")

    print(list_transkrip)
    return list_transkrip

transcribe_streaming_v2(project_id="data-science-programming-ti24",
                        api_key="./gcloud_apikey.json",
                        audio_file="./Donald Trump.mp3")
