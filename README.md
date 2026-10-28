# Last-Mile Delivery Route Adherence: Analyzing Distance Deviation and Time-Window Compliance

This project analyzes last-mile logistics route data to evaluate how actual route execution compares with planned routes. The analysis focuses on stop-sequence adherence, distance deviation, time-window performance, driver variation, and route complexity.

The objective is to identify patterns in route execution and examine whether deviations from planned stop sequences are associated with excess distance and lower time-window adherence.

Tools and Workflow

Python (pandas, NumPy, SciPy, Matplotlib): Data validation, transformation, exploratory analysis, metric calculation, statistical testing, and visualization.

Power Query: Data verification and normalization.

Footnotes

1. The 75th percentile identifies relatively high position_deviation_rate and distance_deviation, while the 25th percentile identifies low time_adherence_rate. These thresholds support exploratory segmentation, not absolute operational standards. Results depend on the selected cutoffs and do not establish causality or underperformance.

2. Route complexity is assessed using stop_count as a measure of stop workload and planned_distance as a measure of geographic scope. Both are analyzed separately against position_adherence_rate. Other factors, such as traffic and road difficulty, are not captured.

3. time_adherence_rate is the percentage of stops arriving within the inclusive window between Earliest Time and Latest Time. It measures time-window compliance, not additional travel time or delay duration.

4. distance_deviation is actual distance minus planned distance. Positive values indicate excess distance and potential inefficiency, but may also reflect detours, road conditions, or other operational factors.

5. Spearman correlation tests associations between position_deviation_rate and both distance_deviation and time_adherence_rate. Holm correction adjusts for the two tests. Statistical significance does not imply causation or practical importance.

Dataset are sourced from [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S2352340926002970)
