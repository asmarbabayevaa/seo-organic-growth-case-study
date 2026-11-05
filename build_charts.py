"""SEO portfolio charts - built from portfolio_public.csv (indexed data, Aug 2025 = 100)."""
import pandas as pd, matplotlib.pyplot as plt, matplotlib.ticker as mt
import os

CSV = os.environ.get("CSV", "portfolio_public.csv")
OUT = os.environ.get("OUT", "charts")
os.makedirs(OUT, exist_ok=True)

df = pd.read_csv(CSV)
df["date"] = pd.to_datetime(df["month"] + "-01")
def s(seg, col): return df[df.segment == seg].set_index("date")[col]

BRAND, NONB, COMP, OTHER = "brand", "core_non_branded", "competitor_brand", "other_unclassified"
COL = {BRAND: "#7f7f7f", NONB: "#0072B2", COMP: "#D55E00"}
LAB = {BRAND: "Brand queries", NONB: "Non-brand queries (own products & generic lottery)",
       COMP: "Competitor-brand queries"}

plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False,
                     "axes.spines.right": False, "axes.grid": True, "grid.alpha": .25,
                     "axes.titleweight": "bold", "axes.titlesize": 14})
FOOT = "Source: Google Search Console. Aug 2025 = 100. Full months only (Aug 2025 - Oct 2026)."

def finish(fig, ax, title, sub, name, ylabel=None):
    ax.set_title(title, loc="left", pad=22)
    ax.text(0, 1.02, sub, transform=ax.transAxes, fontsize=10, color="#555")
    if ylabel: ax.set_ylabel(ylabel)
    ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("%b\n%Y"))
    fig.text(0.01, -0.02, FOOT, fontsize=8, color="#777")
    fig.tight_layout(); fig.savefig(f"{OUT}/{name}.png", dpi=160, bbox_inches="tight"); plt.close(fig)

def endlabel(ax, series, text, color, dy=0):
    ax.annotate(text, (series.index[-1], series.iloc[-1]), xytext=(6, dy), textcoords="offset points",
                color=color, fontsize=9, va="center", fontweight="bold")

# 1 growth beyond brand
fig, ax = plt.subplots(figsize=(10, 5.6))
for seg in (BRAND, NONB):
    y = s(seg, "clicks_index"); ax.plot(y.index, y, color=COL[seg], lw=2.8 if seg == NONB else 2, label=LAB[seg])
    endlabel(ax, y, f"{y.iloc[-1]:.0f}", COL[seg])
ax.axhline(100, color="#aaa", lw=1, ls="--")
ax.legend(frameon=False, loc="upper left")
n = s(NONB, "clicks_index").iloc[-1]
finish(fig, ax, f"Non-brand organic clicks grew {n-100:.0f}% in 14 months, faster than brand",
       "Clicks index by query type", "01_growth_beyond_brand", "Clicks index")

# 2 clicks vs impressions (growth came from ranking, not reach)
fig, ax = plt.subplots(figsize=(10, 5.6))
c, i = s(NONB, "clicks_index"), s(NONB, "impressions_index")
ax.plot(c.index, c, color="#0072B2", lw=2.8, label="Clicks"); ax.plot(i.index, i, color="#999", lw=2.2, ls="--", label="Impressions")
ax.fill_between(c.index, i, c, where=c > i, color="#0072B2", alpha=.12)
ax.axhline(100, color="#aaa", lw=1); ax.legend(frameon=False, loc="upper left")
finish(fig, ax, "Same audience, more clicks: better rankings turned impressions into traffic",
       "Non-brand queries: clicks vs impressions index", "02_clicks_vs_impressions", "Index")

# 3 position
fig, ax = plt.subplots(figsize=(10, 5.6))
for seg in (NONB, COMP, BRAND):
    y = s(seg, "avg_position"); ax.plot(y.index, y, color=COL[seg], lw=2.6 if seg != BRAND else 1.8, label=LAB[seg])
    endlabel(ax, y, f"{y.iloc[-1]:.1f}", COL[seg])
ax.invert_yaxis(); ax.legend(frameon=False, loc="lower left")
a, b = s(NONB, "avg_position").iloc[0], s(NONB, "avg_position").iloc[-1]
finish(fig, ax, f"Non-brand average position improved from {a:.1f} to {b:.1f}",
       "Average position (impression-weighted; higher on chart = better)", "03_average_position", "Average position")

# 4 top-10 footprint
fig, ax = plt.subplots(figsize=(10, 5.6))
for seg in (NONB, COMP):
    y = s(seg, "queries_top10_index"); ax.plot(y.index, y, color=COL[seg], lw=2.8, label=LAB[seg])
    endlabel(ax, y, f"{y.iloc[-1]:.0f}", COL[seg])
ax.axhline(100, color="#aaa", lw=1, ls="--"); ax.legend(frameon=False, loc="upper left")
k = s(COMP, "queries_top10_index").iloc[-1] / 100
finish(fig, ax, f"Page-one footprint: competitor-brand queries in the top 10 grew {k:.1f}x",
       "Number of ranking queries in the top 10 (index)", "04_top10_footprint", "Queries in top 10 (index)")

# 5 competitor spike
fig, ax = plt.subplots(figsize=(10, 5.6))
y = s(COMP, "clicks_index"); ax.bar(y.index, y, width=22, color="#D55E00", alpha=.35, label="Monthly clicks")
ax.plot(y.index, y.rolling(3, min_periods=1).mean(), color="#D55E00", lw=2.8, label="3-month average")
ax.axvspan(pd.Timestamp("2026-04-20"), pd.Timestamp("2026-06-12"), color="#999", alpha=.12)
ax.set_ylim(0, y.max() * 1.22)
ax.text(pd.Timestamp("2026-05-16"), y.max() * 1.07, "A competitor's\nlottery campaign", ha="center", fontsize=9, color="#444")
ax.legend(frameon=False, loc="upper left")
finish(fig, ax, "Competitor-brand clicks: a one-off spike in May-June, driven by a competitor campaign",
       "Clicks index. The spike is a one-off; rankings (chart 04) are the lasting gain", "05_competitor_spike", "Clicks index")

# 6 click share
fig, ax = plt.subplots(figsize=(10, 5.6))
sh = pd.DataFrame({LAB[BRAND]: s(BRAND, "share_of_total_clicks"), LAB[NONB]: s(NONB, "share_of_total_clicks"),
                   LAB[COMP]: s(COMP, "share_of_total_clicks")})
sh["Other"] = 1 - sh.sum(axis=1)
ax.stackplot(sh.index, [sh[c] * 100 for c in sh.columns], labels=sh.columns,
             colors=[COL[BRAND], COL[NONB], COL[COMP], "#d9d9d9"], alpha=.9)
ax.yaxis.set_major_formatter(mt.PercentFormatter()); ax.set_ylim(0, 100)
ax.legend(frameon=False, loc="lower center", bbox_to_anchor=(.5, -.28), ncol=2)
a, b = sh[LAB[NONB]].iloc[0] * 100, sh[LAB[NONB]].iloc[-1] * 100
finish(fig, ax, f"Non-brand's share of organic clicks rose from {a:.0f}% to {b:.0f}%",
       "Share of total organic clicks", "06_click_share", "Share of clicks")

# 7 YoY table
rows = []
for m in ("08", "09", "10"):
    r = {"Month": pd.Timestamp(f"2026-{m}-01").strftime("%b")}
    for seg in (NONB, COMP, BRAND):
        c = s(seg, "clicks_index"); r[{NONB:"Non-brand\nclicks YoY",COMP:"Competitor-brand\nclicks YoY",BRAND:"Brand\nclicks YoY"}[seg]] = f"{c[pd.Timestamp(f'2026-{m}-01')] / c[pd.Timestamp(f'2025-{m}-01')] - 1:+.0%}"
    p = s(NONB, "avg_position")
    r["Non-brand\navg position"] = f"{p[pd.Timestamp(f'2025-{m}-01')]:.1f} -> {p[pd.Timestamp(f'2026-{m}-01')]:.1f}"
    rows.append(r)
t = pd.DataFrame(rows)
fig, ax = plt.subplots(figsize=(10, 3.0)); ax.axis("off")
tb = ax.table(cellText=t.values, colLabels=t.columns, loc="center", cellLoc="center"); tb.auto_set_font_size(False); tb.set_fontsize(10); tb.scale(1, 2.3)
for (r_, c_), cell in tb.get_celld().items():
    cell.set_edgecolor("#ddd")
    if r_ == 0: cell.set_facecolor("#0072B2"); cell.set_text_props(color="white", fontweight="bold")
ax.set_title("Year over year (same month, 2026 vs 2025): non-brand clicks up 56-71%", loc="left", pad=8)
fig.text(0.01, 0.02, "Source: Google Search Console. Like-for-like months remove seasonality.", fontsize=8, color="#777")
fig.savefig(f"{OUT}/07_year_over_year.png", dpi=160, bbox_inches="tight"); plt.close(fig)
print("done")
