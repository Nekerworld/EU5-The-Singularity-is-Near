# Glorp UI statistics integration

The local compatibility mod adds two rows to Glorp's left statistics panel. Each compact metric has a `show_when` gate: GDP and education appear once cached, industry/labor wait for Age VII (or related institutions / meaningful values), and the public stock index waits for a stock-exchange advance or embracing industrial capitalism. GDP hover shows up to ten annual observations as a horizontal bar chart. K/M/B/T use explicit 10^3/10^6/10^9/10^12 thresholds. The GDP model itself is unchanged.

History is stored in country variables and retained in saves. Annual GDP updates shift the history only when the observation year changes. Repeated recalculation in the same year replaces the latest sample. Old saves seed their first observation on the next monthly country pulse; no past values are invented. Date jumps leave actual observation years on the chart rather than fabricated intervening years.

The UI reads cached variables; it never scans locations or recomputes GDP on hover. The history adds ten bounded country-variable samples. Missing statistics show an em dash. Education and stock history are not retroactively reconstructed.

Workshop GUI source is not copied into this repository. tools/gen_glorp_stats_compat.py generates the two local-only Glorp overrides in the compatibility mod. gen_playset_compat.py also calls it when Glorp is in the selected playset. The override preserves the source's other widgets and adjusts the statistics bar and ribbon heights by 60 pixels. If the upstream layout anchors change, generation stops for review.

Runtime checks after restarting: both rows fit the left panel, the expand/collapse ribbon remains clickable, GDP hover opens the ten-row chart, values use K/M/B/T, the next annual update appends a sample, same-year recalculation does not append, saving/loading preserves history. Static validation cannot establish GUI layout and glue resolution.
