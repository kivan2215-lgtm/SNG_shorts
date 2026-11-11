# SNG 025 — Bluebelle

Self-contained source project for RU and EN vertical documentary previews.

- `ru/`, `en/`: narration, final paced voice, timed words, subtitles, edit list, title/description and quality report.
- `assets/`: archival scans, original generated scene sheets, map data.
- `SOURCES.md`, `asset_manifest.json`: fact decisions, provenance, permissions status and distinctions between photographs, testimony, the captain’s account and reconstructions.
- `voice.py`: saved voice configuration and fresh synthesis when needed.
- `pace.py`: shortens excessive silence and updates word timings.
- `visuals.py`: native 1080×1920 layouts, regional map, chronology and animated yacht cutaway.
- `build.py`: separate language timelines, subtitles, original score and H.264/AAC export.

To rerender from the preserved paced voice and word timings, install Pillow, NumPy and SciPy and make ffmpeg with libass available:

```sh
python build.py ru
python build.py en
```

Each produces `SNG_025_Bluebelle_<RU|EN>_PREVIEW.mp4` with 30 fps, 1080×1920, H.264/yuv420p, stereo AAC 48 kHz and faststart. The same watermark-free vertical master can be reviewed for YouTube Shorts or TikTok. No automatic YouTube publication occurs.

TTS regeneration additionally needs edge-tts with word boundaries. The project’s `voice.py` uses the established channel voices and refreshes the uncut backups. Run `pace.py` after synthesis and before rebuilding; the preserved final `voice.wav` and `words.json` are sufficient for normal repeat renders. The published assets contain the used archival crops, not entire magazine pages. `prepared_index.json` maps them back to their sources and crop coordinates.

Latest request overrides the old general no-label preference: reconstructions in this episode are explicitly labeled. Do not remove these or present the storm as established fact.
