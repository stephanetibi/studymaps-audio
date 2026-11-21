# studymaps-audio

Audio for the StudyMap Bible app (studymaps.org/app). Everything in `audio/` is published to
**https://studymaps.org/audio/** by the workflow `.github/workflows/deploy-audio.yml` (FTPS to InMotion).

The app code and the verse timings stay in the main repository `stephanetibi/studymaps.org`
(`app/books/<book>/timing_<LANG>.json`); this repository holds only the sound files.

## Layout

    audio/<book>/<LANG>/<book>_<CH>_<LANG>.mp3     e.g. audio/genesis/EN/genesis_01_EN.mp3

- `<book>`: lower-case English book name as in the app (`genesis`, `philippians`...).
- `<CH>`: two digits (three for Psalms).
- One mp3 per chapter, mono, 64 kbps. Verses joined with 0.6 s of silence; the timing file gives each verse's start and end.

## Sources

- EN (base version): NaturalReader commercial, voice Christopher, speed 1.0, NAT English from the book's
  Nazarene Master. Per-verse files, batch texts and respellings are kept on Stéphane's Mac in
  `Nazarene Translation/NN_Book/Audio/<LANG>/`.

## Size

GitHub repositories should stay well under a few GB. One language for the whole Bible at 64 kbps mono is
about 2.3 GB, so later languages may get their own repository (studymaps-audio-fr ...).
