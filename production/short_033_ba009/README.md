# SNG 033 — BA009: the invisible threat

New RU/EN documentary Shorts, applying the user-approved Squalus V4 workflow. Full preview videos for user review, not uploaded to YouTube.

1. Read SOURCES.md, assets.json, shot_plan.json and ../SNG_SHORTS_PLAYBOOK/10_APPROVED_SQUALUS_V4_WORKFLOW.md (published project layout).
2. `python voice.py ru` and `python voice.py en`; `python pace.py` trims only excessive middle-of-silence sections, never accelerates speech. Original narration/words remain in *_uncut files.
3. `python build.py ru --audio-only` / `en --audio-only` writes each language's independent timeline and original musical mix.
4. Blender 4.3.2: `blender -b -t 4 --python-exit-code 1 --python scene3d.py -- KIND render`. Kinds: flight, glow, cabin, cockpit, landing, radar, blocked, deposit, clear, glide. Render all static and moving states; validate frames with captions before full export. `render_models.py` is the resumable dynamic-stage runner from this production.
5. `python build.py ru` / `en`: subtitles, full 1080×1920 30fps H.264/AAC MP4, -16 LUFS target, faststart. No repackaged older film.
6. `python qc.py`: whole-file decode, format, black-frame, loudness and caption checks; inspect all encoded scene samples. Actual auditory and visual statuses are separate.

Files include the original voices, musical stems, subtitle timing, source assets/credits, Blender model source and saved scenes, native animation metadata, and QA evidence. Full frames/research pages are local render cache, not publication requirements. Reproduce scene state through Python; .blend is a saved state, not a keyframed full film.

The initial template-migration utility is intentionally not published; build.py is the reviewed production entry point. `fetch_assets.py` downloads sources; preserve the reviewed notes in assets.json.

Dependencies: Python 3.12, requirements.txt, ffmpeg/ffprobe with libx264/libass, DejaVu Sans Bold, Blender 4.3.2. Model generation also needs NumPy in Blender Python (bundled). Run scripts from the project directory.
