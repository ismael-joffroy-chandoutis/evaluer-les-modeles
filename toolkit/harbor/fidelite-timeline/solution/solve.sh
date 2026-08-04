#!/bin/bash
# Solution de reference : sert a verifier que la tache est resolvable.
set -euo pipefail

python3 - <<'PY'
import csv, os
from pathlib import Path

FPS = 25
RACINE = Path(os.environ.get("HARBOR_APP", "/app"))
with open(RACINE / "plans.csv") as f:
    plans = [(r["nom"], int(r["duree_secondes"])) for r in csv.DictReader(f)]

total = sum(d for _, d in plans) * FPS
assets = "\n".join(
    f'    <asset id="r{i+2}" name="{n}" duration="{d*FPS}/{FPS}s" hasVideo="1" format="r1"/>'
    for i, (n, d) in enumerate(plans)
)
clips = "\n".join(
    f'          <asset-clip ref="r{i+2}" name="{n}" duration="{d*FPS}/{FPS}s" start="0s"/>'
    for i, (n, d) in enumerate(plans)
)

xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<fcpxml version="1.11">
  <resources>
    <format id="r1" name="FFVideoFormat1080p25" frameDuration="1/25s" width="1920" height="1080"/>
{assets}
  </resources>
  <library>
    <event name="banc">
      <project name="montage">
        <sequence format="r1" duration="{total}/{FPS}s" tcStart="0s" tcFormat="NDF">
          <spine>
{clips}
          </spine>
        </sequence>
      </project>
    </event>
  </library>
</fcpxml>
"""
open(RACINE / "montage.fcpxml", "w").write(xml)
PY
