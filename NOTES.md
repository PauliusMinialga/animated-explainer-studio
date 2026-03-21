## Bote

 - POST /generate → Mistral generates Manim script + 3-part TTSScript (intro/info/outro) → Manim renders animation → 
returns animation_url + tts_script
 - Removed: tts.py, avatar.py, merge.py, fal-client dep — all Bote's domain
 - Synced with Paul's and Bote's latest pushes

What Bote gets from our endpoint:

 {
   "animation_url": "/files/{job_id}/animation.mp4",
   "tts_script": {
     "intro": "Hey! Let's explore how Fibonacci works...",
     "info": "The code shows a recursive function...",
     "outro": "Recursion breaks problems into smaller parts."
   }
 }

He can feed intro/outro to create_veed_from_script() for avatar clips, and info for the animation voiceover.
