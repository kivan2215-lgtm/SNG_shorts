# SNG Shorts 028 — Ken Rex McElroy

Two separate vertical previews: Russian and American English. Reference settings: SNG_SHORTS_PLAYBOOK, accepted voice intonation preset from episode 16 V2. User brief: street killing witnessed by a crowd, long history of intimidation, grocer survives, conviction and bail, meeting, shooting, conflicting testimony, investigation, unresolved moral dilemma.

## Final editorial decisions
- No exact “40 witnesses”: sources differ. No statement that literally everyone stayed silent; wife's accusation retained.
- No names or portraits of uncharged alleged shooters. No suggested firing positions or invented geographic crime map.
- No glorification of killing. Final question weighs law's failure against unpunished murder.
- Archival identities checked; original crime-scene photo by Don Shrubshell starts video and returns at the killing.
- Contemporary Skidmore photograph explicitly dated 2025, only in decades-later reflection.
- Three realistic illustrative panels support missing scenes, never used as physical evidence. More details in SOURCES.md.

## Rebuild
1. Use cached `ru/voice.wav`, `en/voice.wav`, and `words.json` with approved pace/intonation.
2. `python build.py ru` / `python build.py en` creates ASS/SRT captions, original underscore/SFX, scene manifest, contact sheet, then complete MP4.
3. `python qc.py` decodes both complete files and verifies stream profile, loudness/peak, faststart, black-frame absence, coverage and caption grouping.
4. To recreate speech from scratch: `PYTHONPATH=/workspace/.sng-shorts/tts_ru_v723 /workspace/.sng-shorts/venv/bin/python voice.py ru` (also en), then `python pace.py`. This requires the configured TTS connection. Raw TTS fragments are cached only in the working source; accepted voice.wav and timings are bundled.

## Delivery
SNG_028_Ken_McElroy_RU_PREVIEW.mp4 and SNG_028_Ken_McElroy_EN_PREVIEW.mp4.
1080×1920, 30fps, H264/yuv420p, AAC stereo 48kHz, faststart. Unapproved previews; not uploaded to YouTube. Titles/descriptions/hashtags in per-language metadata.txt and inline handoff.

## Verification limits
Manual visual review of archives, compositions and representative encoded frames; technical full decode and audio checks. Independent human listening review not claimed. User review remains the next step.
