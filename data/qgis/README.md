# QGIS layers

The live map is a QGIS project with two layers: the arena raster as a base, and
a delimited-text layer pointed at `live.csv` that redraws as the robot moves.

| File | Tracked | What it is |
| --- | --- | --- |
| `arena.tif` | yes | Georeferenced raster of the arena, used as the base layer. |
| `lat_long.csv` | **no — you must supply this** | Static lookup of ArUco marker id → latitude, longitude. |
| `live.csv` | no (generated) | Written once per frame with the robot's current position. |

## Supplying `lat_long.csv`

`control_center.py` reads this at start-up and cannot run without it. It is a
headerless three-column file, one row per marker placed on the arena:

```
21,38.9995,-77.0100
22,38.9996,-77.0101
```

The coordinates are whatever you georeferenced `arena.tif` against — read them
off the raster in QGIS at each marker's physical position. Every id that appears
here must be a marker the overhead camera can actually see, including the extra
off-line markers listed as `STATIC_MARKERS` in `control_center/config.py`.

> This file was excluded by a blanket `*.csv` rule in the original `.gitignore`
> and so was never committed. The rule is gone now, so a regenerated table will
> be tracked.

## Setting up the live layer

Add `live.csv` through *Layer → Add Layer → Add Delimited Text Layer*, set the
geometry fields to `lon`/`lat`, then enable a refresh interval under
*Layer Properties → Rendering*.
