# SNG 036 — John Darwin, RU / EN

Status: review previews, not user-approved. No YouTube upload requested.

Reproducible steps (project Python venv, ffmpeg, Blender 4.3.2):
1. `python voice.py ru` and `python voice.py en`; synthesize complete semantic paragraphs with established voices.
2. `python pace.py`; remove only excess inner silence and remap word timings.
3. `blender -b -t 3 --python scene3d.py -- overview`; `blender -b -t 3 --python scene3d.py -- passage --probes` for composition review; omit `--probes` for all native frames.
4. `python build.py ru --stills` and EN equivalent, inspect compositions and captions; omit `--stills` for full renders.
5. `python qc.py`; inspect actual encoded-frame sheets and animation contacts, record manual review separately. Technical tests cannot establish how words sound.
6. Stage source project and two individual MP4s, push, download both published files in full and compare SHA256.

Sources: SOURCES.md and assets.json. Final word-timed scene mapping: shot_plan.json, per-language timeline.json and captions.json. File and source hashes: render_manifest.json. Direct download verification: delivery_verified.json.

No generic subtitle blocks or footage loops. Reuse of the Panama photo is deliberate: first discovery, then identities, then the date contradiction, then the agency publication. The actual image is not altered. No source is claimed to be public domain merely because it is online.

Probe cache reuse (`--reuse-probes`) checks a scene + human-rig source hash. Re-render probes after edits. Current probe views were manually reviewed before launching the full animation; cache-key enforcement was then added without changing geometry.

Runtime used: Blender 4.3.2 (Cycles CPU, 12 samples + denoising, 720×1280 native model frames), FFmpeg 7.1.5, DejaVu Sans Bold from the system fonts. Python dependencies are pinned in requirements.txt. Output is 1080×1920 H.264/yuv420p, 30fps, AAC stereo 48kHz, faststart. External voice synthesis requires network access; completed audio and timings are retained so visual-only revisions do not require new synthesis.
