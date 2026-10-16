import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
data=(root/'outputs/dashboard_data.json').read_text()
html=(root/'src/dashboard.template.html').read_text().replace('@@DATA@@',data.replace('</','<\\/'))
(root/'outputs/dashboard.html').write_text(html)
print('Built outputs/dashboard.html with embedded synthetic data and no external dependencies.')
