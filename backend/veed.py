import fal_client
from elevenlabs.client import ElevenLabs
from enum import Enum
from pathlib import Path
from dataclasses import dataclass
import sys
import os
from pathlib import Path
from dotenv import load_dotenv


IMAGE_PATH = "/Users/bote.schaafsma/Github/veed_hackathon/media/images/file.jpg"


@dataclass
class TTSScript:
    intro: str
    info: str
    outro: str
    id: int


@dataclass
class Video:
    url: str
    format: str


@dataclass
class RequestResponse:
    intro: Video
    info: Path
    outro: Video


class Intonation(Enum):
    SERIOUS = 1
    HAPPY = 2


@dataclass
class Preferences:
    avatar: Path
    intonation: Intonation


def veed_request(audio_url: str, image_url: str):
    return fal_client.run(
        "veed/fabric-1.0",
        arguments={
            "image_url": image_url,
            "audio_url": audio_url,
            "resolution": "480p",
        },
    )


def veed_request_with_files(
    path_to_audio_file: Path, path_to_image_file: Path
) -> Video:
    audio_url = fal_client.upload_file(path_to_audio_file)
    image_url = fal_client.upload_file(path_to_image_file)
    req = veed_request(audio_url, image_url)
    return request_to_link_and_format(req)


def text_to_speech_file(text: str, fileName: str) -> Path:
    load_dotenv()
    apiKey = os.getenv("ELEVEN_LABS_API_KEY")
    if not apiKey:
        sys.exit("API key for eleven labs not found")
    client = ElevenLabs(api_key=apiKey)
    audio = client.text_to_speech.convert(
        text=text,
        voice_id="JBFqnCBsd6RMkjVDRZzb",  # "George" — clear, natural, great for education
        model_id="eleven_turbo_v2_5",  # fastest + cheapest model
        output_format="mp3_44100_128",
    )
    mp3FileName = fileName + ".mp3"
    with open(mp3FileName, "wb") as f:
        for chunk in audio:
            f.write(chunk)
    return Path(mp3FileName)


def request_to_link_and_format(request) -> Video:
    video = request["video"]
    return Video(url=video["url"], format=video["content_type"])


def create_veed_from_script(
    script: TTSScript, preferences: Preferences
) -> RequestResponse:
    intro_audio_file = text_to_speech_file(script.intro, f"intro_{script.id}")
    outro_audio_file = text_to_speech_file(script.outro, f"outro_{script.id}")
    info_audio_file = text_to_speech_file(script.info, f"info_{script.id}")
    intro_video = veed_request_with_files(intro_audio_file, preferences.avatar)
    outro_video = veed_request_with_files(outro_audio_file, preferences.avatar)
    return RequestResponse(intro=intro_video, info=info_audio_file, outro=outro_video)
