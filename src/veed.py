import fal_client
from pathlib import Path
from dataclasses import dataclass


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


def veed_request(audio_url: str, image_url: str):
    return fal_client.run(
        "veed/fabric-1.0",
        arguments={
            "image_url": image_url,
            "audio_url": audio_url,
            "resolution": "480p",
        },
    )


def veed_request_with_files(path_to_audio_file: str, path_to_image_file: str):
    audio_url = fal_client.upload_file(Path(path_to_audio_file))
    image_url = fal_client.upload_file(Path(path_to_image_file))
    return veed_request(audio_url, image_url)


def text_to_speech_file(text: str, fileName: str) -> str:
    return ""


IMAGE_PATH = "/Users/bote.schaafsma/Github/veed_hackathon/media/images/file.jpg"


def create_veed_from_script(script: TTSScript):
    intro_audio_file = text_to_speech_file(script.intro, f"intro_{script.id}")
    outro_audio_file = text_to_speech_file(script.outro, f"outro_{script.id}")
    info_audio_file = text_to_speech_file(script.info, f"info_{script.id}")
    intro_req = veed_request_with_files(intro_audio_file, IMAGE_PATH)
    print(intro_req)
    outro_req = veed_request_with_files(outro_audio_file, IMAGE_PATH)
    print(outro_req)


def request_to_link_and_format(request) -> Video:
    video = request["video"]
    return Video(url=video["url"], format=video["content_type"])
