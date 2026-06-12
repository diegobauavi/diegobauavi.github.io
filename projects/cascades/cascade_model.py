"""
How many people does it take to move the world?
================================================

Granovetter's threshold model on a small-world network. Each person has a
threshold: the share of their neighbors that has to act before they join in.
Thresholds vary, some people move on the faintest signal, others almost never
budge. A small committed group starts active, and the rest decide round by
round by looking at who around them has already moved.

Two things come out of it. First, change spreads as a cascade, slow at the
edges and then sudden once enough neighbors tip. Second, whether the whole
network ends up moving depends sharply on two numbers: how stubborn people are
on average, and how large the committed minority is at the start. Below a
critical size the push dies out. Above it, almost everyone ends up moving. The
threshold for the committed minority lands near the few percent that the
empirical "3.5% rule" points to.

This single file runs the model, renders a styled animation of one cascade,
and saves a summary figure with the two tipping curves.

Run:
    python cascade_model.py

Outputs (written to ../../assets/cascades/):
    cascade_animation.mp4
    poster.png
    tipping_points.png
"""

import os
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.colors as mcolors
from matplotlib import font_manager
import networkx as nx


# --------------------------------------------------------------------------
# Visual style, matched to the inequality project so the two read as a set.
# --------------------------------------------------------------------------
BG = "#14151a"
PANEL = "#1b1d24"
INK = "#e9eaee"
MUTED = "#9aa0ad"
GRID = "#2a2d36"
AMBER = "#e8a13a"
BLUE = "#7fb1de"
RED = "#e0584b"
EDGE = "#2a2d36"

THRESHOLD_CMAP = mcolors.LinearSegmentedColormap.from_list(
    "thr", ["#7fb1de", "#3a4253"]
)

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
class ThresholdCascade:
    """Granovetter threshold dynamics on a Watts-Strogatz small-world graph."""

    def __init__(self, n=140, k=6, rewire=0.12, mean_thr=0.20, sd_thr=0.10,
                 seed_frac=0.04, seed=42):
        self.n = n
        self.rng = np.random.default_rng(seed)
        self.graph = nx.watts_strogatz_graph(n, k, rewire, seed=seed)
        self.neighbors = [np.array(list(self.graph.neighbors(i))) for i in range(n)]

        thr = self.rng.normal(mean_thr, sd_thr, n)
        self.thresholds = np.clip(thr, 0.01, 0.99)

        self.state = np.zeros(n, dtype=int)
        n_seed = max(1, int(round(seed_frac * n)))
        self.state[self.rng.choice(n, n_seed, replace=False)] = 1   # committed minority

        self.states_over_time = [self.state.copy()]

    def step(self):
        new = self.state.copy()
        for i in range(self.n):
            if self.state[i] or self.neighbors[i].size == 0:
                continue
            if self.state[self.neighbors[i]].mean() >= self.thresholds[i]:
                new[i] = 1
        changed = not np.array_equal(new, self.state)
        self.state = new
        self.states_over_time.append(self.state.copy())
        return changed

    def run(self, max_steps=200):
        for _ in range(max_steps):
            if not self.step():
                break
        return self

    def final_fraction(self):
        return self.state.mean()


# --------------------------------------------------------------------------
# Styled animation of one cascade
# --------------------------------------------------------------------------
def render_animation(model, path, poster_path, fps=4, hold=6):
    pos = nx.spring_layout(model.graph, seed=42, k=1.9 / np.sqrt(model.n))
    xy = np.array([pos[i] for i in range(model.n)])
    states = model.states_over_time
    order = list(range(len(states)))
    frames = [0] * hold + order + [order[-1]] * (hold * 2)

    edge_segments = np.array([[pos[a], pos[b]] for a, b in model.graph.edges()])

    fig = plt.figure(figsize=(11, 8.2))
    fig.subplots_adjust(left=0.04, right=0.96, top=0.85, bottom=0.10, hspace=0.32)
    gs = fig.add_gridspec(2, 1, height_ratios=[3.0, 1.0])
    ax_net = fig.add_subplot(gs[0])
    ax_curve = fig.add_subplot(gs[1])
    ax_net.axis("off")
    ax_net.set_aspect("equal")

    from matplotlib.collections import LineCollection
    ax_net.add_collection(LineCollection(edge_segments, colors=EDGE,
                                         linewidths=0.5, alpha=0.5, zorder=1))
    pad = 0.08
    ax_net.set_xlim(xy[:, 0].min() - pad, xy[:, 0].max() + pad)
    ax_net.set_ylim(xy[:, 1].min() - pad, xy[:, 1].max() + pad)

    inactive_colors = THRESHOLD_CMAP(model.thresholds)
    scat = ax_net.scatter(xy[:, 0], xy[:, 1], s=70, zorder=3,
                          edgecolors=BG, linewidths=0.8)
    pct_text = ax_net.set_title("", loc="center", fontsize=15, fontweight="bold")

    n = model.n

    def draw(fi):
        t = frames[fi]
        st = states[t]
        colors = np.where(st[:, None] == 1, np.array(mcolors.to_rgba(AMBER)),
                          inactive_colors)
        sizes = np.where(st == 1, 130, 70)
        scat.set_facecolors(colors)
        scat.set_sizes(sizes)

        pct = st.mean() * 100
        ax_net.set_title(f"{pct:4.1f}% of the network has moved   (round {t})",
                         loc="center", fontsize=15, fontweight="bold", color=INK)

        ax_curve.clear()
        ax_curve.grid(True, alpha=0.25, linewidth=0.6)
        ys = [s.mean() * 100 for s in states[:t + 1]]
        ax_curve.plot(range(t + 1), ys, color=AMBER, linewidth=2.6)
        ax_curve.scatter([t], [ys[-1]], color=AMBER, s=55, zorder=5,
                         edgecolor=BG, linewidth=1)
        ax_curve.axhline(3.5, color=MUTED, linewidth=0.9, linestyle="--")
        ax_curve.text(0.5, 6, "3.5% committed minority", color=MUTED, fontsize=10)
        ax_curve.set_xlim(0, len(states) - 1)
        ax_curve.set_ylim(0, 103)
        ax_curve.set_xlabel("round")
        ax_curve.set_ylabel("% moved")
        return []

    fig.suptitle("A few committed people, and a threshold each: change spreads as a cascade",
                 x=0.04, ha="left", fontsize=16.5, fontweight="bold")

    # Poster: a mid-cascade frame, where the amber/blue mix is most telling
    fractions = np.array([s.mean() for s in states])
    mid = int(np.argmin(np.abs(fractions - 0.5)))
    draw(hold + mid)
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
# Summary: the two tipping curves
# --------------------------------------------------------------------------
def render_summary(path, runs=40, n=140):
    # Panel A: final adoption vs average stubbornness (mean threshold)
    thr_grid = np.linspace(0.05, 0.45, 21)
    a_mean, a_lo, a_hi = [], [], []
    for mt in thr_grid:
        finals = [ThresholdCascade(n=n, mean_thr=mt, seed_frac=0.04,
                                   seed=r).run().final_fraction()
                  for r in range(runs)]
        finals = np.array(finals) * 100
        a_mean.append(finals.mean())
        a_lo.append(finals.min())
        a_hi.append(finals.max())

    # Panel B: final adoption vs size of the committed minority, on a more
    # stubborn network (higher average threshold) so the minority size matters.
    seed_grid = np.linspace(0.005, 0.15, 21)
    b_mean, b_lo, b_hi = [], [], []
    for sf in seed_grid:
        finals = [ThresholdCascade(n=n, mean_thr=0.32, seed_frac=sf,
                                   seed=r).run().final_fraction()
                  for r in range(runs)]
        finals = np.array(finals) * 100
        b_mean.append(finals.mean())
        b_lo.append(finals.min())
        b_hi.append(finals.max())

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    fig.subplots_adjust(left=0.07, right=0.97, top=0.80, bottom=0.15, wspace=0.24)

    ax1.fill_between(thr_grid * 100, a_lo, a_hi, color=BLUE, alpha=0.15,
                     label=f"range across {runs} runs")
    ax1.plot(thr_grid * 100, a_mean, color=BLUE, linewidth=2.8,
             label=f"average of {runs} runs")
    ax1.set_xlabel("average threshold  (how stubborn people are)")
    ax1.set_ylabel("% of network that ends up moving")
    ax1.set_ylim(0, 103)
    ax1.set_title("Stubbornness has a tipping point", loc="left",
                  fontsize=13, fontweight="bold")
    ax1.legend(loc="lower left", fontsize=9, framealpha=0, labelcolor=INK)
    ax1.grid(True, alpha=0.25, linewidth=0.6)

    ax2.fill_between(seed_grid * 100, b_lo, b_hi, color=AMBER, alpha=0.15,
                     label=f"range across {runs} runs")
    ax2.plot(seed_grid * 100, b_mean, color=AMBER, linewidth=2.8,
             label=f"average of {runs} runs")
    ax2.axvline(3.5, color=RED, linewidth=1.4, linestyle="--")
    ax2.text(3.7, 8, "3.5%", color=RED, fontsize=12)
    ax2.set_xlabel("size of the committed minority  (% of network)")
    ax2.set_ylabel("% of network that ends up moving")
    ax2.set_ylim(0, 103)
    ax2.set_title("So does the size of the committed few", loc="left",
                  fontsize=13, fontweight="bold")
    ax2.legend(loc="lower right", fontsize=9, framealpha=0, labelcolor=INK)
    ax2.grid(True, alpha=0.25, linewidth=0.6)

    fig.suptitle(f"Same model, {runs} runs per point: small changes near the edge flip the whole outcome",
                 x=0.07, ha="left", fontsize=15.5, fontweight="bold")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"saved {path}")


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.normpath(os.path.join(here, "..", "..", "assets", "cascades"))
    os.makedirs(out, exist_ok=True)

    model = ThresholdCascade(n=140, mean_thr=0.20, seed_frac=0.04, seed=11).run()
    print(f"cascade reached {model.final_fraction() * 100:.1f}% "
          f"in {len(model.states_over_time) - 1} rounds")

    render_animation(model,
                     os.path.join(out, "cascade_animation.mp4"),
                     os.path.join(out, "poster.png"))
    render_summary(os.path.join(out, "tipping_points.png"))
    print("done")
