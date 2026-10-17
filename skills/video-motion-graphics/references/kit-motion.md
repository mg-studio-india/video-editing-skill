# Motion and composition rules from the kit

Ported from the forked kit (16:9 talking-head work). The HyperFrames contract itself lives in its own skills (`hyperframes-core`, `hyperframes-animation`, `hyperframes-keyframes`); these are the hard-won house rules on top.

## Composition skeleton

```html
<div id="stage" data-composition-id="..." data-start="0" data-duration="D"
     data-fps="30" data-width="1920" data-height="1080">
  <div class="video-wrapper" id="video-wrap">     <!-- push-over moves (format 3b) -->
    <div id="video-zoom">                          <!-- the camera -->
      <video id="bg-video" src="input-video.mp4" playsinline data-has-audio="true"
             data-start="0" data-duration="D" data-track-index="1"></video>
      <div id="behind-layer"> ...text behind you... </div>
      <video id="fg-matte" src="subject-matte.webm" playsinline muted
             data-start="0" data-duration="D" data-track-index="2"></video>
    </div>
  </div>
  <div class="card-host clip" id="host-card-01" data-card-id="card-01" data-anchor="spoken phrase"
       data-start="..." data-duration="..." data-track-index="3"
       style="left:0;top:0;width:1920px;height:1080px;visibility:hidden;opacity:0;">...</div>
</div>
```

Two nested wrappers on purpose: `#video-wrap` carries push-over moves, `#video-zoom` the camera; two moves on one
element conflict and fail QA. What must ride the camera (footage, text behind you, matte) lives inside `#video-zoom`;
front cards stay outside so they never scale.


## Animating glass (read before writing any entrance)

**Never fade a glass element through an ancestor's `opacity`:** Chrome drops `backdrop-filter` while any ancestor is
below opacity 1, so the frosted panel is missing for the whole fade and snaps in late. Hold the host at opacity 1 and
animate the look of the glass:

```js
tl.set('#host', { visibility:'visible', opacity:1 }, t);
tl.fromTo(glassSel,
  { backgroundColor:'rgba(255,255,255,0)', borderColor:'rgba(255,255,255,0)',
    boxShadow:'0 24px 80px rgba(0,0,0,0)', x:60 },
  { backgroundColor:'rgba(255,255,255,0.18)', borderColor:'rgba(255,255,255,0.58)',
    boxShadow:'0 24px 80px rgba(0,0,0,0.38)', x:0, duration:.42, ease:'power2.out' }, t);
tl.fromTo(contentSel, { opacity:0 }, { opacity:1, duration:.36 }, t + 0.04);   // text is safe to fade
```

The blur is live from frame one but invisible without tint, so this reads as a fade with panel, border and copy arriving
together; the exit reverses it. Copy sitting directly in the glass element needs an inner span to fade. Plain opacity
fades are fine without backdrop-filter (lower lines). Glass that has not arrived stays hidden, or it blurs the footage.

## Traps that waste a render

**Long renders**
- **Disk capture stores every frame first:** 12 minutes at 4K asked for ~714 GB of scratch. Over ~2 minutes, stream the
  encode with one worker (`PRODUCER_STREAMING_ENCODE_MAX_DURATION_SECONDS=3600`, `--workers 1`; ~35 minutes for 12
  minutes of 4K). Parallel streaming painted the footage BLACK for long stretches; `--low-memory-mode` is not the fix.
- **A long single-session 4K capture can hang** in Chrome's screenshot call. Over ~5 minutes, render segmented with a
  fresh browser per segment and keep `--resume` for a retry: `HF_SEGMENTED_CAPTURE=true HF_SEGMENT_FRAMES=1500
  HF_SEGMENT_BROWSER_RECYCLE=1` plus the streaming settings (8:53 rendered clean in 30 minutes).
- **Black footage under parallel workers:** `--workers 1`, and run `ffmpeg -i out.mp4 -vf
  "scale=192:-2,blackdetect=d=0.4:pix_th=0.08" -an -f null -` on every long render.
- **The frame cache fills the temp folder** (16 GB in a day) at `<tmpdir>/hyperframes-extract-cache-<uid>`: delete it
  when no render runs, or move it with `--frames-cache-dir`. Before an assembly, check free disk (about 2 x minutes x
  0.34 GB). Delete the `work-*` folder a failed run leaves; zsh aborts an `&&` chain on an empty glob (`work-*(N)`).
- **A note on a long render costs a patch, not a re-render:** `window-patch.py --public "$W/public" --t0 T0 --t1 T1 --out
  "$W/patch-a"`, rendered with the same flags, then overlaid on the full render (`overlay` with
  `enable='between(t,T0,T1)'`) or spliced in frame-exact (12 ms audio fades). Start the window before the card's host
  enters; prove alignment with `psnr` on the first and last frames (50 dB or more = the same frame). Anything held
  across a splice must be static on both sides.

**Encoding and files**
- **`--gpu` ignores CRF** (`--quality high --gpu` gave 14 Mb/s at 4K): always `--video-bitrate 45M`.
- **The render drops two colour tags:** always the BT.709 remux, or faces look redder than the camera original.
- **Skipping `assemble.py`:** the render keeps the camera level (~-25 LUFS). Level the voice to -14 first (a one-segment
  `assembly.json` does it), then add music; measure the file with `ebur128`.
- **The render finishes; the file can still be wrong** (black footage, a missing tag, audio a frame short):
  `verify-render.py` catches these, the pre-render sheet cannot. Its 40 Mb/s floor fails on mostly still screens
  (hardware encoders undershoot); if every other line passes, that is not a quality problem.

**Composition**
- **Every timed element needs `class="clip"`** or it shows for the whole video. Keep `data-has-audio="true"` on the
  footage (`video_missing_muted` is real) or the render is silent.
- **A second `<video>` on `input-video.mp4` does not paint:** cut the span to its own file and give it a `z-index` above
  `.card-host` (10). **One root composition per `public/`:** a backup inside it doubles the audio.
- **Never put CSS translate(), scale() or rotate() in the style of an element GSAP also moves:** GSAP replaces the whole
  value and the lint fails. Start states go in a `tl.fromTo`; lasting centring goes in the separate CSS `translate` property.
- **A count-up is an `onUpdate` on a proxy tweened on the one timeline;** write the start value in at load.
- **Text that changes step by step (typing, a clock) comes from one proxy tween, never a `tl.set` per step,** which
  leaves letters behind on a backward seek: tween `{ n: 0 }` to the length with `ease: 'none'` and write `slice(0,
  floor(n))`. The check for the whole class: seek past a beat, seek back inside it, compare with a fresh seek.
- **Heavy overlays have a budget:** `composition_heavy_overlay_count_high` counts every `filter: blur`,
  `radial-gradient` and `clip-path`, hidden ones included; around 40 and the capture paints black for the first half
  (every full-frame wash counts). Compose long form per section; prefer `box-shadow` glows.
- **The linter is wrong twice:** `text_occluded` behind the subject is the point, and `text_not_painted` fires on
  `background-clip:text`, which renders fine. Two text blocks in one rebuilt logo box trip `content_overlap` (draw the
  small word with `::before`); an SVG with `width="1em"` renders 16 px (give explicit width and height).

**Fonts, transcription, snapshots**
- **The house font look:** the three 7 KB `assets/fonts/DMSans-{400,500,700}.woff2` subsets under the stack `"DM Sans",
  ui-sans-serif, system-ui, sans-serif`, so Chrome draws in the system face (San Francisco on a Mac) at these metrics.
  That is the approved look; the full variable DM Sans reads rounder and wider. Body `font-family` lists concrete names,
  never a CSS variable, and a scene element never sets `"DM Sans"` alone (a whole scene once rendered in Times).
- **Snapshot filenames:** `snapshot --at 8.0` writes `frame-00-at-8s.png` (no ".0") and wipes the folder each run; copy
  by exact name (`snap-beats.py` does).

