import fal_client
import pyttsx3
import time
import random
import asyncio
import base64
import requests
from runware import Runware, IAudioInference, IAudioSpeech
from elevenlabs.client import ElevenLabs
from enum import Enum
from pathlib import Path
from dataclasses import dataclass
import sys
import os
from dotenv import load_dotenv


IMAGE_PATH = "/Users/bote.schaafsma/Github/veed_hackathon/media/images/file.jpg"
TEMP_FOLDER = "homework"


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


class Avatar(Enum):
    SUPER_MAN = 1
    WONDER_WOMAN = 2
    C3PO = 3


def veed_request(audio_url: str, image_url: str):
    return fal_client.run(
        "veed/fabric-1.0",
        arguments={
            "image_url": image_url,
            "audio_url": audio_url,
            "resolution": "480p",
        },
    )


def avatar_to_image_path(avatar: Avatar) -> Path:
    match avatar:
        case Avatar.SUPER_MAN:
            return Path("media/super_man.jpg")
        case Avatar.WONDER_WOMAN:
            return Path("media/wonder_woman.jpg")
        case Avatar.C3PO:
            return Path("media/c3po.jpg")


def veed_request_with_files(
    path_to_audio_file: Path,
    avatar: Avatar,
) -> Video:
    audio_url = fal_client.upload_file(path_to_audio_file)
    path_to_avatar_file = avatar_to_image_path(avatar)
    image_url = fal_client.upload_file(path_to_avatar_file)
    req = veed_request(audio_url, image_url)
    return request_to_link_and_format(req)


def text_to_speech_file(text: str, fileName: str) -> Path:
    load_dotenv()
    apiKey = os.getenv("RUNWARE_API_KEY")
    if not apiKey:
        raise Exception()

    try:

        async def _runware_tts():
            runware = Runware(api_key=apiKey)
            await runware.connect()
            request = IAudioInference(
                model="inworld:tts@1.5-mini",  # Runware Inworld TTS-1.5 Mini
                speech=IAudioSpeech(
                    text=text,
                    voice="Oliver",  # Default voice
                ),
            )
            results = await runware.audioInference(requestAudio=request)
            await runware.disconnect()
            return results

        results = asyncio.run(_runware_tts())
        if results and len(results) > 0:
            audio = results[0]
            mp3FileName = fileName + ".mp3"
            if audio.audioURL:
                resp = requests.get(audio.audioURL)
                with open(mp3FileName, "wb") as f:
                    f.write(resp.content)
            elif audio.audioBase64Data:
                with open(mp3FileName, "wb") as f:
                    f.write(base64.b64decode(audio.audioBase64Data))
            return Path(mp3FileName)
    except Exception as e:
        print(f"Runware TTS error: {e}. Falling back to pyttsx3.")
        raise e

    # Fallback to pyttsx3
    # engine = pyttsx3.init()
    # mp3File = fileName + ".mp3"
    # engine.save_to_file(text, mp3File)
    # engine.runAndWait()


def request_to_link_and_format(request) -> Video:
    video = request["video"]
    return Video(url=video["url"], format=video["content_type"])


def create_veed_from_script(script: TTSScript, avatar: Avatar) -> RequestResponse:
    os.mkdir(TEMP_FOLDER)
    intro_audio_file = text_to_speech_file(
        script.intro, f"{TEMP_FOLDER}/intro_{script.id}"
    )
    outro_audio_file = text_to_speech_file(
        script.outro, f"{TEMP_FOLDER}/outro_{script.id}"
    )
    info_audio_file = text_to_speech_file(
        script.info, f"{TEMP_FOLDER}/info_{script.id}"
    )
    intro_video = veed_request_with_files(intro_audio_file, avatar)
    outro_video = veed_request_with_files(outro_audio_file, avatar)
    return RequestResponse(intro=intro_video, info=info_audio_file, outro=outro_video)


# if __name__ == "__main__":
#     random.seed(time.time() * 1000)
#     response = create_veed_from_script(
#         script=TTSScript(
#             intro="Hello and welcome to your first vizify video. We are here to help you tackle every challenge you face. Carrying you where need. Have fun.",
#             info="Normally this part is slightly longer. I will keep it short for now.",
#             outro="That was it, have a great day and I hope to see you again soon.",
#             id=random.randint(0, 1_000_000_000),
#         ),
#         avatar=Avatar.SUPER_MAN,
#     )
#     print(response)
