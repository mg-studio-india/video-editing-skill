# whisper.cpp setup (macOS)

Everything runs locally. The only optional network step is `yt-dlp` fetching a video you give it a URL for.

## 1. Install

```
brew install ffmpeg whisper-cpp
brew install yt-dlp                  # optional: URL input for reference videos
python3 -m pip install pillow        # optional: contact sheets (much cheaper for the agent to read)
```

If pip refuses with "externally managed environment", use `python3 -m pip install --user pillow` or a virtual environment. Python 3.8+ is enough; the macOS system Python works.

## 2. Download the model

The large model is about 3 GB:

```
mkdir -p ~/.cache/whisper.cpp
curl -L -o ~/.cache/whisper.cpp/ggml-large-v3.bin \
  https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3.bin
```

The skill finds it automatically in `~/.cache/whisper.cpp/`, `~/whisper.cpp/models/` and a few other usual places. Otherwise set `WATCH_WHISPER_MODEL`.

`ggml-large-v3-turbo.bin` is a faster alternative with a small accuracy trade-off; it needs a reasonably recent whisper.cpp build (the Homebrew one is). Point `WATCH_WHISPER_MODEL` at it to use it.

## 3. Check

```
python3 "$ENG/scripts/watch.py" check
```

Everything required should read `OK`. On Apple Silicon the Homebrew build normally uses the GPU through Metal; whisper-cli's startup lines will say so.

## 4. Verify word timing once on your own clip

Word timestamps are the foundation of the cut list and captions, so check them once:

```
python3 "$ENG/scripts/transcribe_cpp.py" some_clip.mp4 --end 20
```

It prints the first words with their times. They should increase steadily and line up with what you hear. If many words share identical times, try `WATCH_WHISPER_DTW=large.v3` (token-level alignment for the large-v3 model) and `--fresh`. If your build does not know a flag, the skill drops it and retries rather than failing.

## 5. Configuration

`python3 "$ENG/scripts/setup.py" --init-config` writes a commented `~/.config/watch/.env`. Environment variables override it.

| Variable | Default | Use |
|---|---|---|
| `WATCH_WHISPER_CPP_BIN` | auto (`whisper-cli`) | Path to the binary |
| `WATCH_WHISPER_MODEL` | auto (large-v3) | Path to the ggml model |
| `WATCH_WHISPER_LANG` | `auto` | Force a language code (`en`, `hi`, ...). Whisper picks one language per file, so set it explicitly for code-switched speech |
| `WATCH_WHISPER_PROMPT` | empty | Initial prompt: names, jargon. Also **keeps fillers**: `Um, uh, you know, I mean, like.` |
| `WATCH_WHISPER_DTW` | empty | Optional `--dtw` alignment preset such as `large.v3` |
| `WATCH_WHISPER_THREADS` | min(8, cores) | CPU threads |
| `WATCH_SCENE_THRESHOLD` | `0.20` | Cut sensitivity (lower finds softer cuts) |
| `WATCH_CACHE_DIR` | `~/.cache/watch` | Where artifacts and the transcript cache live |

## 6. Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `Transcript: none` plus a warning | whisper-cli or the model is missing; run `$ENG/scripts/watch.py check` and follow the fix lines |
| `whisper-cli finished but wrote no JSON` | Build is too old for `-oj`; `brew upgrade whisper-cpp` |
| Filler count is 0 on talky footage | Whisper omits fillers by default; set `WATCH_WHISPER_PROMPT` and re-run with `--fresh` |
| Words missing in music-heavy sections | Normal for speech models; trust the audio and the sound-cue list over the words there |
| Transcript repeats the same phrase | Whisper loops on silence/music; the skill collapses obvious loops (`loops_collapsed` in `analysis.json`) |
| No contact sheets, many single frames | Pillow not installed; `python3 -m pip install pillow` |
| URL fails | yt-dlp missing or the site needs cookies; download the file yourself and pass the path |
| Slow transcription | large-v3 is the most accurate and the slowest; it only runs once per file (cached). Use the turbo model for drafts |
