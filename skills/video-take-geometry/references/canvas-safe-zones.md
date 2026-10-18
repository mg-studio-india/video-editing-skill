# Canvas Geometry & Safe Zones

From the 225-style catalog appendix. Every layout, caption and card placement respects these margins; `video-render`
uses the same canvas sizes.


```
+-----------------------------------------------------------------------------------------------------+
| CANVAS ASPECT RATIO MATRIX & SAFE MARGIN CONTRACT                                                    |
+-----------------------------------------------------------------------------------------------------+
| Dimension     | Pixels (W x H)  | Safe Margins (Copy & Face Limits)         | Pipeline Skill Engine |
+---------------+-----------------+-------------------------------------------+-----------------------+
| Vertical 9:16 | 1080 x 1920 px  | Top: 180px, Bottom: 280px, Sides: 80px    | video-take-geometry   |
| Square 1:1    | 1080 x 1080 px  | Uniform 60px all sides                    | stage.py (square)     |
| Portrait 4:5  | 1080 x 1350 px  | Top: 80px, Bottom: 140px, Sides: 60px     | stage.py (portrait)   |
| Landscape 16:9| 1920 x 1080 px  | Title-safe 5% (96px horizontal, 54px vert)| compose.py (16:9 kit) |
| Cinematic     | 2560 x 1080 px  | Ultra-wide 2.39:1 scope letterbox         | cinematic conform     |
| Transparent   | Custom (RGBA)   | Alpha matte channel (ProRes 4444 / WebM)  | npx hyperframes alpha |
+-----------------------------------------------------------------------------------------------------+
```
