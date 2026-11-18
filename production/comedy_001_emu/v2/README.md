# SNG Comedy001 — Emu War, V2

Revision requested 18 November 2026: more absurdity, uncensored profanity and connected narration. See REVISION.md. Based on real1932 events, original dry profane humor. RU/EN previews pending user approval. Existing documentary thriller style remains separate.

## Deliverables
- `SNG_COMEDY_001_EMU_RU_PREVIEW_V2.mp4`
- `SNG_COMEDY_001_EMU_EN_PREVIEW_V2.mp4`
- Narration, aligned word events, ASS/SRT, metadata, source manifest, render source and Blender scenes.

## Rebuild
Use the existing workspace venv with edge-tts, NumPy, Pillow and requests; FFmpeg/FFprobe, Blender4.3.2 and DejaVuSans.
1. `python voice.py ru` and `python voice.py en` (networkTTS; cached by paragraph/text/voice settings).
2. `python pace.py` cuts excessive silence only; rebuilds all word timings.
3. `blender -b -t 4 -P scene3d.py -- scatter`, then `-- truck`. Twelve-sample denoised Cycles,720×1280source, native30fps. No optical interpolation.
4. `python build.py ru --stills` and `python build.py en --stills`; inspect composites and `python preflight.py`.
5. `RENDER_FINAL=1 python build.py ru`, same foren. Source models must be complete; strict production flag rejects missing frames.
6. `python qc.py`; inspect encoded sample sheets and record auditory status separately.
7. Save project/MP4s via `stage_project.py`; publish to authorizedGitHub repository; `python verify_delivery.py` downloads full public files and compares hashes.

## Style
34 semantic shots per language, expressive approved narrators, quiet original comic music, absurd editorial comments,4unique historical photographs,13original illustrated scenes,2original animated dioramas. No corpse images, animal pain sounds, camera shake or constant zoom.

Current limits: no full auditory review. Stylized diagrams are not measured historical terrain or exact weapon/vehicle models. Original archival photographs are low resolution and not claimed to beHD. Generated actors are illustrative, not historical portraits. Photo metadata and rights basis are inSOURCES.md/ assets.json.

## V2 verification
RU 81.233333 seconds; EN 72.5 seconds. Full decode, format, caption-range, black-frame and loudness checks passed. 102 encoded visual samples per language reviewed. No full auditory review; preview pending user approval.
