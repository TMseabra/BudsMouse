# Physical test checklist

1. Pair the Buds in Windows; disconnect from phone / Galaxy Wearable.
2. `python phase2_sensors.py MAC` with buds outside the case - expect GRV lines.
3. Put buds in the case, lid open - repeat.
4. Close the lid - repeat; note whether the link drops.
5. `python phase3_mouse.py MAC --dry-run` and move the case; check dx/dy directions.
