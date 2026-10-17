# Style fingerprint

`fingerprint.json` is the compact, reusable profile of how a video is edited. The measured parts are filled by `watch.py`; you fill `qualitative` after looking at the frames. Pass a finished reference fingerprint to `mine --against` and to `compare`.

## Measured fields (do not edit)

| Block | Fields | Meaning |
|---|---|---|
| `pacing` | `cuts_per_minute`, `mean/median/p10/p90_shot_length`, `pace`, `soft_transition_share`, `curve_cuts_per_minute`, `hook.{first_shot_duration,cuts_in_first_3s,cuts_in_first_10s}` | How fast it cuts, how that changes over time (curve), and how busy the opening is |
| `speech` | `words_per_minute`, `time_to_first_word`, `pauses_per_minute`, `longest_pause`, `fillers_per_minute`, `speech_coverage` | Delivery speed, how soon speech starts, how tight the pauses are |
| `video-audio` | `integrated_lufs`, `loudness_range_lu`, `true_peak_dbtp`, `silence_ratio`, `longest_silence` | Loudness target and how much silence it tolerates |
| `cut_alignment` | `counts`, `j_or_l_share`, `on_pause_share` | Whether cuts hide in pauses or overlap speech (heuristic) |
| `visual` | `black_frame_runs`, `static_share` | Fades/black beats and how much of the picture is static |

`curve_cuts_per_minute` has one value per `curve_window_seconds`. Read it for shape: a front-loaded curve means a busy hook that relaxes; a rising curve means building energy.

## Qualitative fields (you fill these)

Estimate from the sheets; say `null` only if you cannot tell. Prefer short, comparable values.

| Field | Fill with |
|---|---|
| `hook_type` | One of the hook patterns in `storyboard-schema.md` |
| `hook_text` | The actual opening words (from the transcript) |
| `structure` | List of beats with time ranges, e.g. `["hook 0-3s", "setup 3-12s", "demo 12-40s", "CTA 40-45s"]` |
| `framing_mix` | Rough shares, e.g. `"65% CU talking head, 25% screen, 10% b-roll"` |
| `camera_movement` | e.g. `"static + frequent punch-ins"` |
| `b_roll_ratio` | 0-1 estimate of runtime that is not the main subject |
| `on_screen_text` | Style, placement and frequency of titles/callouts |
| `caption_style` | `present` (true/false), `position`, `words_per_caption` (a number, since `mine` uses it), `emphasis`, `font_feel` |
| `transitions_used` | Which techniques appear and how often |
| `zoom_punch_ins` | Frequency and size, e.g. `"every 3-4s, ~110%"` |
| `music` | `present`, `mood`, `ducking_under_voice` |
| `color_grade` | Contrast/saturation/temperature in a few words |
| `notes` | Anything that makes this video distinctive |

Fields that would be `null` because they genuinely do not apply (no captions, no music) should say so explicitly (`present: false`) rather than stay null, so lint passes honestly.

## Reading `compare` / `mine --against`

Verdicts are `similar` (within tolerance), `higher`, `lower`, or `n/a` (not measurable in one of the videos). Tolerances are deliberately loose (about 25% on pacing, 0.5s on time-to-first-word, 1.5 LU on loudness). Translate each non-similar row into an edit action:

- Cuts per minute **lower** than reference → add visual changes: punch-ins, cutaways, on-screen text.
- Time to first word **higher** → cut the lead-in.
- Pauses per minute / longest pause **higher** → tighten with the tight-cut list.
- Loudness off → normalise (`loudnorm`), check true peak.
- J/L share **lower** → consider letting audio lead or trail picture at cuts to smooth rhythm.

Never present a similar/different verdict as quality: it only says "matches the reference", which is the user's goal only if they chose that reference deliberately.
