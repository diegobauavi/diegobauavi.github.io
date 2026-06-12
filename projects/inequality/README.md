# Compounding and inequality

A minimal simulation of how extreme inequality emerges from multiplicative
growth alone, even when the per-round advantage is fair and reshuffled every
few rounds.

Everyone starts with one coin. Each round, wealth is multiplied by `(1 + t)`,
where `t` is drawn from a normal distribution. Every few rounds the values of
`t` are drawn again from scratch, so nobody keeps a permanent edge. Inequality
still rises sharply, and the link between current skill and accumulated wealth
fades to almost nothing.

## Run

```bash
pip install numpy matplotlib   # ffmpeg must be on your PATH for the video
python inequality_model.py
```

This writes three files to `../../assets/inequality/`:

- `wealth_animation.mp4` — one run over 120 rounds
- `poster.png` — the final frame (also used as the video poster)
- `summary.png` — Gini, skill-wealth correlation, and a Lorenz curve across 60 runs

Everything lives in the single file `inequality_model.py`.
