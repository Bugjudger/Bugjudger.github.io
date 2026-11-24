# Research previews

Local review draft, 2026-11-24. Original papers and supplementary videos remain
unchanged. Preview files use authentic source assets; schematic overlays are noted
below. No manuscript PDF is included in the site.

## Source material

| Work | Source / additional hover information |
| --- | --- |
| RecurrentVLM | Illustrative shell game rendered with the original VET-Bench Three.js scene from https://github.com/liutiedong/shellgame; hidden-ball tracking and reveal, not an evaluation result |
| IDWorld | Figure 1: one observed person, side/back pixel references, and predicted latent features |
| PuppetGait | Figure 2: three actual RGB frames, recovered bodies, and source/canonical LVM features |
| VideoResearcher | Figure 3 authentic video frames; Section 3.3 tool implementation, validation, and retention illustrated as Build → Test → Reuse |
| Clue-OPSD | arXiv:2608.25356v1 Figure 1: sampled clue frames and actual full-video / clue-only car-count answers |
| InstantHDR | Original `InstantHDR/videos/bear/instanthdr.mp4`, cropped to 444×296 at (2,110) |
| FoundationGait | Figure 3 Gait3D Rank-1 results; fixed GaitSSB baseline with FoundationGait scaling curve drawn on hover |
| GaitMax | Figure 3: original RGB input and six aligned learned attention maps (legs, feet, arms) |
| BiggerGait | Figures 1(c), 2 and Section 3.5: native layer planes → separate gait features → combined layer evidence |
| SapiensID | Figure 7 matching/nonmatching face-body pairs and part similarities |
| BigGait | Original animated WebP: walking RGB plus all-purpose, silhouette, parsing, and skeleton representations |
| GaitEditer | arXiv:2303.05076v1 Figure 7 original silhouettes and size/hoodie/hat edits |

`sources.json` contains original extraction coordinates. `hover-evidence.json`
records evidence and animation timings.
`scripts/build_evidence_previews.py` rebuilds the SVG previews. Temporary paper
renders / the local IDWorld source package are needed only when cached crops are
missing. Viewing the site never fetches paper assets from those locations.

## Composition and motion

All previews share a 3:2 canvas, a subtle #f4f4f4 background, and no border.
Desktop thumbnails are 210×140 CSS pixels; narrow-screen thumbnails are 104px
wide at the same ratio. Static and hover states occupy exactly the same frame.
The publication grid adapts the fixed-media-column structure from
https://jonbarron.info/stylesheet.css, with a 234px desktop column and
20px image-to-text spacing. The research introduction is 17px; desktop paper
text is 17px with more breathing room between entries.

IDWorld retains one observation plus side/back pixel-reference views. The two
reference people are 10% smaller; their visible foreground bounds determine the
latent-map display boxes, keeping head/feet, center, and size aligned. Hover
reveals the latent comparison in 0.6s and holds it until pointer leave.

PuppetGait uses an RGB input, recovered 3D body, and canonical feature map.
Head/torso/foot correspondence markers move in a 2.6s loop. Both body states use
one fixed display rectangle and the marker coordinates use the same transforms.
Markers illustrate correspondence rather than measured transport trajectories.

BigGait uses the final walking sequence of the original animated WebP. The RGB
input and four original representations are rearranged into the same 3:2 canvas
without stretching. The original 70ms delays are shortened to 40ms; title/end
holds are omitted. `scripts/build_biggait_original_preview.py` rebuilds it and
`biggait-original-preview.json` records frame indices and crops.

VideoResearcher keeps only short tool-development labels. Its “Toolbox +1” is an
illustration of retaining an accepted update, not an experimental measurement.

PuppetGait loops in 2.6s and VideoResearcher in 4.8s; IDWorld reveals once on hover. Other SVG
previews use 0.45s transitions and shortened reading holds. All begin from their
static cover with no opening hold. Leaving restores the cover; returning restarts
from the first frame. Keyboard Enter/Space and touch taps also toggle playback.
Reduced-motion preference keeps previews static.

## Loading and file size

Animation bytes load only after hover, tap, or keyboard activation and are cached
for reuse. Scrolling does not prefetch animations. The static cover stays visible
until the first animation frame is decoded, avoiding an empty image while loading.

- RecurrentVLM GIF: 439,812 bytes; 360×240, 4.28s. Only frame timing changed.
- InstantHDR GIF: 728,533 bytes; 240×160, 48 frames, 4.8s. Rebuilt from the original
  video at 10fps with a 128-color palette; about 51% smaller than the earlier GIF.
- Both GIF posters are lossless WebP exports of their exact first frames.
- BigGait animated WebP: 147,766 bytes, 360×240, 20 frames, 0.8s. Exact decoded-first-frame static cover.
- SVG hover previews are approximately 28–221 KB each, before HTTP compression.

`gif-preview-timing.json` records GIF timing/encoding details. Full-resolution
original sources remain unchanged; rejected review iterations are kept in ignored
local backups.

Where to Look Matters places “Full video” above the filmstrip.

FoundationGait shows the complete GaitSSB baseline and its own 6M starting point.
On hover, its measured performance curve draws through 10M, 30M, and 130M in
1.2 seconds, then holds until pointer leave. The parameter axis is logarithmic.

BigGait loops original frames 160–178 only; frame 179 is an end-title card and
is excluded. The static cover is the exact decoded first animation frame.

GaitMax retains the original 32×64 input and part-attention outputs from Figure 3.
The RGB view stays fixed; left/right query responses crossfade between legs, feet,
and arms in a 2.5-second loop. These are query views of one frame, not temporal
trajectories. All three panels retain the same native aspect ratio and body scale.

BiggerGait reuses the original paper input and green layer planes. Four representative
layers stand for the sampled LVM layers. Hover traces separate extraction branches
and accumulates their contributions in a shared decision, then holds. Colored
strips are schematic contributions, not measured feature maps; the paper averages
layer-wise distances at ensemble testing. The thumbnail does not depict a new
learned fusion network. No performance chart is shown.

SapiensID keeps a fixed reference portrait. Figure 7 upper-right/lower-right
photo candidates and their real part-similarity maps crossfade together in a
2.4-second loop. All three slots stay fixed at the same scale. Native tiny
similarity-score and colorbar labels are hidden, keeping the actual maps.

GaitEditer uses 13 native edits from Figure 7, beginning with the stronger skirt
and outfit examples. Original/edited pairs are recorded in `gaitediter-edit-cases.json`
and verified using PDF image placement (stream order is not column order).
The 9.36-second loop advances every 0.72 seconds with a 0.16-second crossfade.
Each pair preserves the native 44×64 geometry; the original changes with the
source subject. The 195° and 270° examples begin from the third subject at 60°.
