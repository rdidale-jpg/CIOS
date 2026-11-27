"""Accessible financial charts over explicitly scoped presentation values."""
from decimal import Decimal
from html import escape


def value_label(value):
    return format(value, ',')


def bars(title, basis, rows, *, target=None, waterfall=False, suffix=''):
    """Rows are (label, signed value). The chart has one native inspection link."""
    if not rows:
        return ''
    intervals = []
    running = Decimal(0)
    for _, value in rows:
        end = running + value if waterfall else value
        intervals.append((running, end))
        if waterfall:
            running = end
    low = min(0, *(min(pair) for pair in intervals))
    high = max(0, *(max(pair) for pair in intervals))
    span = high - low or 1

    def position(value):
        return 20 + float((value - low) / span) * 280

    height = 34 * len(rows)
    graphics = [f'<line x1="{position(0):.1f}" x2="{position(0):.1f}" y1="0" y2="{height}" stroke="#748477"/>']
    for index, ((_, value), (start, end)) in enumerate(zip(rows, intervals)):
        y = 7.5 + 34 * index
        left = position(min(start, end))
        width = abs(position(end) - position(start))
        colour = '#93442f' if value < 0 else '#226350'
        graphics.append(f'<rect x="{left:.1f}" y="{y}" width="{max(1, width):.1f}" height="19" rx="2" fill="{colour}"/>')
    label = escape(title)
    plot = (f'<div class="finance-plot"><svg viewBox="0 0 320 {height}" preserveAspectRatio="none" aria-hidden="true" focusable="false">'
            + ''.join(graphics) + '</svg></div>')
    labels = ''.join('<li><span>' + escape(name) + '</span><strong>' +
                     escape(value_label(value) + suffix) + '</strong></li>' for name, value in rows)
    content = f'<h3>{label}</h3><p>{escape(basis)}</p><div class="finance-bars">{plot}<ol>{labels}</ol></div>'
    if target:
        content = f'<a class="finance-chart-link" href="{escape(target, quote=True)}">{content}</a>'
    return '<section class="finance-chart">' + content + '</section>'
