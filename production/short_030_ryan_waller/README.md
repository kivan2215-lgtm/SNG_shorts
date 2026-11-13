# SNG 030 — Ryan Waller

Two vertical preview cuts, RU and EN. 1080×1920, 30 fps, H.264/AAC, faststart.

A seven-second audible interrogation excerpt follows the account of the shooting. It uses the original recording sound and translated Russian captions in the RU version. The other archive excerpts play under the documentary narration. The source's embedded English captions are retained. See `SOURCES.md` for provenance, source times and distinctions between archives and illustrations.

Voices: ru-RU-DmitryNeural and en-US-GuyNeural. To reproduce, use `edge-tts==7.2.3`; version 7.3.1 failed to return audio for most Russian text in this environment. Load the environment CA bundle via SSL_CERT_FILE. The completed audio is included, so re-synthesis is unnecessary.

Pipeline: voice.py → pace.py → insert_dialogue.py → build.py LANGUAGE → qc.py. Do not rerun pace or insertion over already edited audio; raw backups stay in the working project. The working source video is 200 MB and is not committed to GitHub. Download `_c_lmx4LdNw.mp4` from the archive.org source in SOURCES.md as `assets/interrogation_source.mp4` to rebuild. The crop removes existing pillarboxing; it preserves the original interrogation scene and faces.

The source recording has no medically graphic scene. No invented police dialogue is used. The educational brain illustration is not the patient's scan or a measured bullet trajectory. The unknown cause of death is not asserted.
