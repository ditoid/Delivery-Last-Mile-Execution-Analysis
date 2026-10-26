import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as stats
from statsmodels.stats.multitest import multipletests

df = pd.read_csv("logist_dataset.csv")

#core question
"""
Is route sequence deviation significantly associated with distance deviation and time-window adherence
"""

#business question
"""
How closely do actual routes follow planned stop sequences?
How does route sequence deviation relate to distance deviation and time-window adherence?
Which routes have high sequence deviation and high distance deviation?
How does route adherence vary by driver?
Does route complexity affect adherence to the planned sequence?
"""

#For Business Question 1 to 3 its 1 Route per column
#Business Question 1
route_adherence_count = (
    df
    .assign(
        route_adherent = lambda x: np.where(
            x["IndexP"] == x["IndexA"],
            1,
            0
        )
    )
    .groupby("Route ID")
    .agg(
        planned_count = ("route_adherent", "sum"),
        stop_count = ("Route ID", "count")
    )
    .assign(
        position_adherence_rate = lambda x: x["planned_count"] / x["stop_count"] * 100,
        position_deviation_rate = lambda x: 100 - x["position_adherence_rate"]
    )
)

#Business Question 2
distance_defined  = (
    df
    .assign(
        distance_difference = lambda x: x["DistanceA"] - x["DistanceP"]
    )
    .groupby("Route ID")
    .agg(
        planned_distance = ("DistanceP", "sum"),
        actual_distance = ("DistanceA", "sum"),
        distance_deviation = ("distance_difference", "sum")
    )
)

time_status_defined = (
    df
    .assign(
        #Boolean filtering for time
        early=lambda x: x["Arrived Time"] < x["Earliest Time"],
        late=lambda x: x["Arrived Time"] > x["Latest Time"],
        on_time=lambda x: (
            (x["Arrived Time"] >= x["Earliest Time"]) &
            (x["Arrived Time"] <= x["Latest Time"])
        )
    )
    .groupby("Route ID")
    .agg(
        early_stop=("early", "sum"),
        late_stop=("late", "sum"),
        on_time_stop=("on_time", "sum"),
        total_stop = ("Route ID", "count")
    )
    .assign(
        time_adherence_rate = lambda x: x["on_time_stop"] / x["total_stop"] * 100
    )
)

#Business Question 3
route_metrics = (
    route_adherence_count
    .merge(distance_defined, on="Route ID")
    .merge(time_status_defined, on="Route ID")
).reset_index()

metrics_describe = (
    route_metrics[["position_deviation_rate", "distance_deviation", "time_adherence_rate"]]
    .describe(percentiles= [0.25, 0.50, 0.75, 0.90, .95])
)

share_dist_filter = (
    route_metrics
    .assign(
        high_actual_sh = lambda x:
            x["position_deviation_rate"] >= x["position_deviation_rate"].quantile(0.75),
        high_dist_dev = lambda x:
            x["distance_deviation"] >= x["distance_deviation"].quantile(0.75)
     )
     .loc[
         lambda x: x["high_actual_sh"] & x["high_dist_dev"]
     ]
)

share_time_filter = (
    route_metrics
    .assign(
        high_actual_sh = lambda x:
            x["position_deviation_rate"] >= x["position_deviation_rate"].quantile(0.75),
        low_time_adh = lambda x:
            x["time_adherence_rate"] <= x["time_adherence_rate"].quantile(0.25)
     )
     .loc[
         lambda x: x["high_actual_sh"] & x["low_time_adh"]
     ]
)

#Business Question 4
route_adherence_driver = (
    df
    .assign(
        route_adherent = lambda x: np.where(
            x["IndexP"] == x["IndexA"],
            1,
            0
        )
    )
    .groupby("Driver ID")
    .agg(
        planned_count = ("route_adherent", "sum"),
        stop_count = ("Route ID", "count")
    )
    .assign(
        position_adherence_rate = lambda x: x["planned_count"] / x["stop_count"] * 100,
        position_deviation_rate = lambda x: 100 - x["position_adherence_rate"]
    )
)

#Business Question 5
distance_adherence = (
    route_metrics
    .assign(
        dist_bucket = lambda x:
            pd.qcut(
                x["planned_distance"],
                q=4,
                duplicates="drop"
            )
    )
    .groupby("dist_bucket")
    .agg(
        avg_adherence = ("position_adherence_rate", "mean"),
        route_count = ("Route ID", "nunique")
    )
)

route_stop_adherence = (
    route_metrics
    .assign(
        route_bucket = lambda x:
            pd.qcut(
                x["stop_count"],
                q=4,
                duplicates="drop"
            )
    )
    .groupby("route_bucket")
    .agg(
        avg_adherence = ("position_adherence_rate", "mean"),
        route_count = ("Route ID", "nunique")
    )
)

#Hypothesis and correlation testing
spearman_distance = (
    stats.spearmanr(route_metrics["position_deviation_rate"], route_metrics["distance_deviation"])
)

spearman_time = (
    stats.spearmanr(route_metrics["position_deviation_rate"], route_metrics["time_adherence_rate"])
)

#Holm's
p_values = [
    spearman_distance.pvalue,
    spearman_time.pvalue
]

reject, p_adjusted, _, _ = multipletests(
    p_values,
    alpha=0.05,
    method="holm"
)

print("Reject H0:", reject)
print("Adjusted p-values:", p_adjusted)

#Visualization
#Distance scatterplot
plt.figure(figsize=(8, 5))

plt.scatter(
    route_metrics["position_deviation_rate"],
    route_metrics["distance_deviation"]
)
plt.xlabel("position deviation pct")
plt.ylabel("distance deviation")
plt.title("route deviation vs distance deviation")

plt.show()

#Time adherence scatterplot
plt.figure(figsize=(8, 5))

plt.scatter(
    route_metrics["position_deviation_rate"],
    route_metrics["time_adherence_rate"]
)
plt.xlabel("position deviation pct")
plt.ylabel("time adherence pct")
plt.title("route deviation vs time adherence")

plt.show()