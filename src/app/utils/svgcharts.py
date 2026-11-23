"""Tiny server-side SVG bar charts.

Used for the progress charts (FR-14) so the page needs no external chart
library or network access. Values come straight from stored records.
"""


def bar_chart(rows, width=640, height=220, unit=""):
    """Render a labelled bar chart.

    rows: list of (label, value) pairs. Returns an SVG string, or an empty
    string when there is nothing to plot (the template shows the empty
    state instead).
    """
    rows = [(label, float(value)) for label, value in rows]
    if not rows or not any(value for _, value in rows):
        return ""
    top = max(value for _, value in rows)
    pad_l, pad_b, pad_t = 44, 34, 12
    plot_w = width - pad_l - 8
    plot_h = height - pad_b - pad_t
    n = len(rows)
    slot = plot_w / n
    bar_w = max(4, min(slot * 0.6, 60))

    parts = [
        '<svg viewBox="0 0 %d %d" role="img" xmlns="http://www.w3.org/2000/svg">'
        % (width, height),
        '<line class="axis" x1="%d" y1="%d" x2="%d" y2="%d"/>'
        % (pad_l, pad_t + plot_h, pad_l + plot_w, pad_t + plot_h),
        '<text x="4" y="%d" font-size="10">%g%s</text>'
        % (pad_t + 4, top, unit),
    ]
    # Label only some days when the period is long, so text stays readable.
    step = max(1, n // 8)
    for i, (label, value) in enumerate(rows):
        bar_h = plot_h * value / top if top else 0
        x = pad_l + slot * i + (slot - bar_w) / 2
        y = pad_t + plot_h - bar_h
        if bar_h:
            parts.append(
                '<rect class="bar" x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3">'
                "<title>%s: %g%s</title></rect>" % (x, y, bar_w, bar_h, label,
                                                    value, unit))
        if i % step == 0 or i == n - 1:
            parts.append(
                '<text x="%.1f" y="%d" font-size="9" '
                'text-anchor="middle">%s</text>'
                % (pad_l + slot * i + slot / 2, height - pad_b + 12, label))
    parts.append("</svg>")
    return "".join(parts)
