"""
Compounding and inequality: one small model
===========================================

A minimal experiment. Everyone starts with the same wealth. Each round, a
person's wealth is multiplied by (1 + t), where t is a "return on what you
have" drawn from a normal distribution. Every few rounds the values of t are
drawn again from scratch, so nobody keeps a permanent edge. Think of it as
handing the skill (or the luck) back to a hat and dealing it out again, the
way fortune resets across generations.

The point of the experiment: even when the advantage is temporary and shared
out fairly every few rounds, multiplicative growth alone drives the population
into extreme inequality, and the link between current skill and accumulated
wealth fades to almost nothing.

This single file runs the model, renders a styled animation, and saves a
summary figure with the ensemble results.

Run:
    python inequality_model.py

Outputs (written to ../../assets/inequality/):
    wealth_animation.mp4
    poster.png
    summary.png
"""

import os
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import font_manager


# --------------------------------------------------------------------------
# Visual style. Dark, restrained, a single warm accent. Tuned to sit next to
# the website rather than look like a default matplotlib export.
# --------------------------------------------------------------------------
BG = "#14151a"
PANEL = "#1b1d24"
INK = "#e9eaee"
MUTED = "#9aa0ad"
GRID = "#2a2d36"
AMBER = "#e8a13a"
CORAL = "#e8744f"
BLUE = "#7fb1de"
RED = "#e0584b"

STYLE = {
    "figure.facecolor": BG,
    "savefig.facecolor": BG,
    "axes.facecolor": PANEL,
    "axes.edgecolor": GRID,
    "axes.labelcolor": MUTED,
    "axes.titlecolor": INK,
    "text.color": INK,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "grid.color": GRID,
    "axes.grid": True,
    "axes.axisbelow": True,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "font.size": 13,
}


def _pick_font():
    """Use a clean sans if the system has one, otherwise leave the default."""
    for name in ("Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"):
        try:
            font_manager.findfont(name, fallback_to_default=False)
            return name
        except Exception:
            continue
    return None


_FONT = _pick_font()
if _FONT:
    STYLE["font.family"] = _FONT
plt.rcParams.update(STYLE)


# --------------------------------------------------------------------------
# The model
# --------------------------------------------------------------------------
class WealthModel:
    """Multiplicative wealth growth with periodically reshuffled returns."""

    def __init__(self, n=1000, steps=120, mu=0.05, sigma=0.10,
                 reshuffle_every=5, seed=None):
        self.n = n
        self.steps = steps
        self.mu = mu                      # mean return per round
        self.sigma = sigma                # spread of returns across people
        self.reshuffle_every = reshuffle_every
        self.rng = np.random.default_rng(seed)

        self.wealth = np.ones(n)
        self.skill = self._draw_skill()

        self.wealth_history = [self.wealth.copy()]
        self.gini_history = [self._gini()]
        self.corr_history = [0.0]
        self.top1_history = [self._top_share(0.01)]

    def _draw_skill(self):
        t = self.rng.normal(self.mu, self.sigma, self.n)
        return np.maximum(t, -0.99)       # a round can't wipe out more than the stake

    def _gini(self):
        w = np.sort(self.wealth)
        total = w.sum()
        if total == 0:
            return 0.0
        idx = np.arange(1, self.n + 1)
        return float((2 * np.sum(idx * w)) / (self.n * total) - (self.n + 1) / self.n)

    def _corr(self):
        if np.std(self.skill) == 0 or np.std(self.wealth) == 0:
            return 0.0
        c = np.corrcoef(self.skill, self.wealth)[0, 1]
        return 0.0 if np.isnan(c) else float(c)

    def _top_share(self, frac):
        w = np.sort(self.wealth)
        k = max(1, int(frac * self.n))
        total = w.sum()
        return float(w[-k:].sum() / total) if total > 0 else 0.0

    def step(self, t):
        if t > 0 and t % self.reshuffle_every == 0:
            self.skill = self._draw_skill()     # hand the returns back to the hat
        self.wealth = self.wealth * (1.0 + self.skill)
        self.wealth = np.maximum(self.wealth, 1e-9)   # stay above a tiny floor
        self.wealth_history.append(self.wealth.copy())
        self.gini_history.append(self._gini())
        self.corr_history.append(self._corr())
        self.top1_history.append(self._top_share(0.01))

    def run(self):
        for t in range(1, self.steps + 1):
            self.step(t)
        return self


# --------------------------------------------------------------------------
# Styled animation
# --------------------------------------------------------------------------
def render_animation(model, path, poster_path, fps=24, n_frames=220):
    frames = np.linspace(0, model.steps, n_frames, dtype=int)

    fig = plt.figure(figsize=(13, 7.3))
    fig.subplots_adjust(left=0.07, right=0.97, top=0.84, bottom=0.11,
                        wspace=0.28, hspace=0.45)
    gs = fig.add_gridspec(2, 2, height_ratios=[1.25, 1.0])
    ax_dist = fig.add_subplot(gs[0, :])
    ax_gini = fig.add_subplot(gs[1, 0])
    ax_corr = fig.add_subplot(gs[1, 1])

    log_all = np.log10(np.maximum(model.wealth_history[-1], 1e-9) + 1)
    x_max = max(1.0, float(np.percentile(log_all, 99.5)) * 1.05)
    bins = np.linspace(0, x_max, 46)

    def draw(i):
        t = frames[i]
        for ax in (ax_dist, ax_gini, ax_corr):
            ax.clear()
            ax.grid(True, alpha=0.25, linewidth=0.6)

        wealth = model.wealth_history[t]
        logw = np.log10(wealth + 1)

        # Top: where everyone sits on a log wealth axis
        ax_dist.hist(logw, bins=bins, color=AMBER, alpha=0.9,
                     edgecolor=BG, linewidth=0.6)
        ax_dist.set_xlim(0, x_max)
        ax_dist.set_xlabel("wealth (log scale)")
        ax_dist.set_ylabel("people")
        ax_dist.set_title("Where the wealth sits", loc="left",
                          fontsize=14, fontweight="bold", pad=10)
        share = model.top1_history[t] * 100
        ax_dist.text(0.985, 0.9,
                     f"round {t:>3}\ntop 1% holds {share:4.1f}%",
                     transform=ax_dist.transAxes, ha="right", va="top",
                     color=INK, fontsize=12.5,
                     bbox=dict(boxstyle="round,pad=0.5", fc=PANEL, ec=GRID))

        # Bottom left: inequality climbing
        ax_gini.plot(range(t + 1), model.gini_history[:t + 1],
                     color=RED, linewidth=2.6)
        if t >= 0:
            ax_gini.scatter([t], [model.gini_history[t]], color=RED,
                            s=55, zorder=5, edgecolor=BG, linewidth=1)
        ax_gini.set_xlim(0, model.steps)
        ax_gini.set_ylim(0, 1)
        ax_gini.set_xlabel("round")
        ax_gini.set_ylabel("Gini")
        ax_gini.set_title("Inequality", loc="left", fontsize=13,
                          fontweight="bold", pad=8)

        # Bottom right: skill-wealth link fading
        ax_corr.plot(range(t + 1), model.corr_history[:t + 1],
                     color=BLUE, linewidth=2.6)
        ax_corr.scatter([t], [model.corr_history[t]], color=BLUE,
                        s=55, zorder=5, edgecolor=BG, linewidth=1)
        ax_corr.set_xlim(0, model.steps)
        ax_corr.set_ylim(-0.15, 1.0)
        ax_corr.axhline(0, color=MUTED, linewidth=0.8, linestyle=":")
        ax_corr.set_xlabel("round")
        ax_corr.set_ylabel("skill vs wealth")
        ax_corr.set_title("Does skill still explain wealth?", loc="left",
                          fontsize=13, fontweight="bold", pad=8)

        fig.suptitle("Everyone starts equal. Returns are reshuffled every "
                     f"{model.reshuffle_every} rounds. Inequality still wins.",
                     x=0.07, ha="left", fontsize=16.5, fontweight="bold")
        return []

    draw(len(frames) - 1)
    fig.savefig(poster_path, dpi=150)

    anim = animation.FuncAnimation(fig, draw, frames=len(frames),
                                   interval=1000 / fps, blit=False)
    writer = animation.FFMpegWriter(fps=fps, bitrate=3600,
                                    metadata={"artist": "Diego Bautista Aviles"})
    anim.save(path, writer=writer, dpi=110)
    plt.close(fig)
    print(f"saved {path}")
    print(f"saved {poster_path}")


# --------------------------------------------------------------------------
# Summary figure across many runs
# --------------------------------------------------------------------------
def render_summary(path, runs=60, n=1000, steps=120, seed0=0):
    ginis, corrs = [], []
    sample = None
    for r in range(runs):
        m = WealthModel(n=n, steps=steps, seed=seed0 + r).run()
        ginis.append(m.gini_history)
        corrs.append(m.corr_history)
        if r == 0:
            sample = m
    ginis = np.array(ginis)
    corrs = np.array(corrs)
    x = np.arange(steps + 1)

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 4.6))
    fig.subplots_adjust(left=0.06, right=0.97, top=0.80, bottom=0.16, wspace=0.3)

    # Gini across runs
    ax1.fill_between(x, ginis.min(0), ginis.max(0), color=RED, alpha=0.15)
    ax1.plot(x, ginis.mean(0), color=RED, linewidth=2.6)
    ax1.set_ylim(0, 1)
    ax1.set_xlabel("round")
    ax1.set_ylabel("Gini")
    ax1.set_title(f"Inequality climbs in every run ({runs} runs)",
                  loc="left", fontsize=12.5, fontweight="bold")
    ax1.grid(True, alpha=0.25, linewidth=0.6)

    # Correlation across runs
    ax2.fill_between(x, corrs.min(0), corrs.max(0), color=BLUE, alpha=0.15)
    ax2.plot(x, corrs.mean(0), color=BLUE, linewidth=2.6)
    ax2.axhline(0, color=MUTED, linewidth=0.8, linestyle=":")
    ax2.set_ylim(-0.2, 1.0)
    ax2.set_xlabel("round")
    ax2.set_ylabel("skill vs wealth")
    ax2.set_title("Skill stops explaining wealth", loc="left",
                  fontsize=12.5, fontweight="bold")
    ax2.grid(True, alpha=0.25, linewidth=0.6)

    # Lorenz curve of the final state of one run
    w = np.sort(sample.wealth_history[-1])
    cum_w = np.cumsum(w) / w.sum()
    cum_p = np.linspace(0, 1, len(w))
    ax3.plot([0, 1], [0, 1], color=MUTED, linewidth=1.3, linestyle="--")
    ax3.plot(cum_p, cum_w, color=AMBER, linewidth=2.8)
    ax3.fill_between(cum_p, cum_p, cum_w, color=AMBER, alpha=0.18)
    ax3.set_xlim(0, 1)
    ax3.set_ylim(0, 1)
    ax3.set_xlabel("share of people")
    ax3.set_ylabel("share of wealth")
    ax3.set_title(f"Lorenz curve  (Gini = {sample.gini_history[-1]:.2f})",
                  loc="left", fontsize=12.5, fontweight="bold")
    ax3.grid(True, alpha=0.25, linewidth=0.6)

    fig.suptitle("Same rules, sixty runs: the pattern is the rule, not the exception",
                 x=0.06, ha="left", fontsize=15.5, fontweight="bold")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"saved {path}")


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.normpath(os.path.join(here, "..", "..", "assets", "inequality"))
    os.makedirs(out, exist_ok=True)

    model = WealthModel(n=1000, steps=120, seed=7).run()
    print(f"final Gini = {model.gini_history[-1]:.3f}, "
          f"top 1% holds {model.top1_history[-1] * 100:.1f}%, "
          f"skill-wealth corr = {model.corr_history[-1]:.3f}")

    render_animation(model,
                     os.path.join(out, "wealth_animation.mp4"),
                     os.path.join(out, "poster.png"))
    render_summary(os.path.join(out, "summary.png"))
    print("done")
