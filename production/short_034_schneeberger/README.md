# SNG 034 — two languages, one source project

A new true-crime scenario replacing the aviation direction rejected by the user. Preserve the approved Squalus V4 / BA009 modeling-and-caption workflow, but prioritize a contradiction, escalating evidence, a delayed explanation and a debatable factual ending. This is a full preview for user review, not an approved final or a YouTube upload.

Read SOURCES.md, assets.json and shot_plan.json before reuse. Read ../SNG_SHORTS_PLAYBOOK/README.md and 10_APPROVED_SQUALUS_V4_WORKFLOW.md for persistent preferences.

1. Python3.12 and requirements.txt; ffmpeg/ffprobe with libx264 and libass; DejaVu Sans Bold; Blender4.3.2.
2. `python voice.py ru` / `en`; cache by paragraph. Delete changed paragraph cache before regeneration. `python pace.py` uses original audio and remaps all words after trimming only excessive silence.
3. `python build.py ru --audio-only` / `en --audio-only`: independent timeline and original score.
4. `blender -b -t 4 --python-exit-code 1 --python scene3d.py -- KIND`. Kinds: lab, lab_close, clinic, clinic_close, folder, car, balm, hair, arm_closed, arm_open, court, folder_motion. The last kind has31 native action frames and checked background caching. The static batch script renders eleven static models. Cached probes may only be reused with identical geometry/material/camera/light settings for that branch.
5. `python build.py ru --stills` / `en --stills`; inspect actual model+annotation layout. Then `python build.py ru` / `en` produces complete1080×1920 MP4 with subtitles and -16LUFS target.
6. `python qc.py`: whole-file decode, format, black-frame, loudness, subtitle and faststart checks, plus start/middle/end samples of every encoded shot. Inspect the samples; automated tests do not replace semantic review.

Keep the original recordings, word boundaries, pauses, script, source credits, Blender scenes, animation metadata and final MP4. Generated frame caches and full third-party research pages are not included in the public project. Regenerate them from the reviewed source.
