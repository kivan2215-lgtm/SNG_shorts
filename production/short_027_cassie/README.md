# SNG 027 — bilingual source project

Run `python build.py ru` and `python build.py en` with ffmpeg/libass, Pillow and NumPy. Retained voice.wav and words.json reproduce the accepted timing. voice.py uses established voices; pace.py updates timing after trimming excessive silence. visuals.py contains all layouts and diagrams. assets includes photos, official court PDF, rendered first page and generated scenes. sources.json and SOURCES.md distinguish archive, generated imagery and reported events. Files are previews for user review.


## V2 archive footage revision
Original school greeting and library planning excerpts now replace four still-image segments in both languages. Narration, score and captions unchanged. Download the source specified in assets/tape_source.json into assets/original_tape.mp4 (verify SHA256); place the V1 preview in its language folder and run `python insert_archive.py ru` / `en`. Source 4:3 aspect preserved without cropped faces or added motion. QC_V2.json covers published files.
