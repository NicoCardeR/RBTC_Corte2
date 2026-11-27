#!/usr/bin/env python3
import math, re, subprocess
t = subprocess.run(["gz", "topic", "-e", "-t", "/world/dif_bot_world/pose/info", "-n", "1"],
                   capture_output=True, text=True).stdout
i = t.index('name: "dif_bot"')
v = [float(x) for x in re.findall(r"[xyzw]: (-?[0-9.]+(?:e[+-]?[0-9]+)?)", t[i:i + 700])[:7]]
print("x=%.3f  y=%.3f  yaw=%.1f deg" % (v[0], v[1], math.degrees(2 * math.atan2(v[5], v[6]))))
