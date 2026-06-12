# How many people does it take to move the world?

Granovetter's threshold model on a Watts-Strogatz small-world network. Each
person has a threshold: the share of their neighbors that must already be
active before they join. A small committed minority starts active, and the
rest decide round by round.

Two tipping points fall out of it. The final outcome depends sharply on how
stubborn people are on average, and on how large the committed minority is at
the start. The committed-minority threshold lands near the empirical "3.5%
rule".

## Run

```bash
pip install numpy matplotlib networkx   # ffmpeg must be on your PATH for the video
python cascade_model.py
```

This writes three files to `../../assets/cascades/`:

- `cascade_animation.mp4` — one cascade spreading across the network
- `poster.png` — a mid-cascade frame (also the video poster)
- `tipping_points.png` — final adoption vs average threshold, and vs committed-minority size

Everything lives in the single file `cascade_model.py`.
