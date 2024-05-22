import queue
import re
import sys
import sounddevice as sd
import numpy as np
import soundfile as sf

from google.cloud import speech
from google.oauth2 import service_account

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms

class AudioStream:
    """Opens a recording stream as a generator yielding the audio chunks."""

    def __init__(self, rate=RATE, chunk=CHUNK):
        self.rate = rate
        self.chunk = chunk
        self.closed = True

    def __enter__(self):
        self.closed = False
        return self

    def __exit__(self, *args):
        self.closed = True

    def generator(self):
        with sd.InputStream(channels=1, samplerate=self.rate, blocksize=self.chunk,
                             dtype='int16', latency='low') as stream:
            while not self.closed:
                data = stream.read(self.chunk)
                yield data


def listen_print_loop(responses):
    """Iterates through server responses and prints them."""
    num_chars_printed = 0
    for response in responses:
        if not response.results:
            continue

        # The `results` list is consecutive. For streaming, we only care about
        # the first result being considered, since once it's `is_final`, it
        # moves on to considering the next utterance.
        result = response.results[0]
        if not result.alternatives:
            continue

        # Display the transcription of the top alternative.
        transcript = result.alternatives[0].transcript

        # Display interim results, but with a carriage return at the end of the
        # line, so subsequent lines will overwrite them.
        #
        # If the previous result was longer than this one, we need to print
        # some extra spaces to overwrite the previous result
        overwrite_chars = " " * (num_chars_printed - len(transcript))

        if not result.is_final:
            sys.stdout.write(transcript + overwrite_chars + "\r")
            sys.stdout.flush()

            num_chars_printed = len(transcript)

        else:
            print(transcript + overwrite_chars)

            # Exit recognition if any of the transcribed phrases could be
            # one of our keywords.
            if re.search(r"\b(exit|quit)\b", transcript, re.I):
                print("Exiting..")
                break

            num_chars_printed = 0

    return transcript


def main():
    """Transcribe speech from audio file."""
    # See http://g.co/cloud/speech/docs/languages
    # for a list of supported languages.
    # language_code = "id-ID"  # a BCP-47 language tag
    language_code = "en-US"  # a BCP-47 language tag

    credentials = service_account.Credentials.from_service_account_file('gcloud_apikey.json')
    client = speech.SpeechClient(credentials=credentials)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code=language_code,
        model="latest_long"
    )

    streaming_config = speech.StreamingRecognitionConfig(
        config=config, interim_results=True, single_utterance=True
    )

    with AudioStream(RATE, CHUNK) as stream:
        audio_generator = stream.generator()
        requests = (
            speech.StreamingRecognizeRequest(audio_content=content)
            for content in audio_generator
        )

        responses = client.streaming_recognize(streaming_config, requests)

        # Now, put the transcription responses to use.
        listen_print_loop(responses)

if __name__ == "__main__":
    main()
