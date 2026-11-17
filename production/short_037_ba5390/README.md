# SNG 037 — BA5390 — bilingual review previews

Status: complete project under production/review, not user approved. Separate RU/EN1080x1920/30fps H264 yuv420p AAC48k stereo faststart. Narration determines duration; no global speed-up. Read SOURCES.md and metadata.txt.

## Reproduction

Use project venv dependencies (requirements.txt), FFmpeg7.x, Blender4.3.2. Narrators ru-RU-DmitryNeural and en-US-GuyNeural, inherited five-paragraph intonation/rates. Existing synthesis files are cached by text/voice/rate/pitch hash; native voice service still required for uncached synthesis.

1. `python voice.py ru`, `python voice.py en`; then `python pace.py` (cuts silence only; remaps word timings).
2. `blender -b -t 3 -P scene3d.py -- window --probes` and `... -- bolts --probes`. Inspect initial/intermediate/end states with overlays. Run without `--probes` to render full native sequences; `--reuse-probes` checks source hash.
3. `python build.py ru --stills` and EN to produce timeline/subtitles/contact sheets; `python preflight.py` adds actual ASS captions to sample scene frames.
4. Full `python build.py ru` and EN, or `finish_render.py` waits for complete processed model caches before builds and technical QA.
5. `python qc.py`, review all encoded contact sheets and motion samples; preserve separate auditory flag. Files are PREVIEW until user approval.

## Graphics

Original generated vertical scenes, actual photographs (full context preserved), actual report/bolt comparison. Subject-specific 3D window frame and three threaded fasteners, smooth native30fps window displacement and comparison rotation, no optical flow or constant camera zoom. Window37frames (1.2s movement then hold) and bolts61frames (2s turn then hold). Rendering720x1280, text/composite1080x1920. A short clear movement is appropriate to pressure failure; whole assembly and fasteners stay in frame. Diagram approximate, not flight physics or a repair blueprint.

## Persistence / limitations

Source code, narration, timing, music, source art, Blender scenes, manifests and QA retained. Rejected drafts and reference videos remain local. Do not publish credentials or the user's third-party reference videos. No YouTube upload. Technical QC does not equal listening; audible pronunciation has not been independently checked here. Publication via authorised public GitHub MP4 files; full remote download verified separately before links supplied.
