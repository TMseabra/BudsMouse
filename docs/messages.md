# Message IDs used so far

| ID  | Name                    | Direction | Notes |
|-----|-------------------------|-----------|-------|
| 97  | EXTENDED_STATUS_UPDATED | buds->PC  | sent on connect |
| 124 | SET_SPATIAL_AUDIO       | PC->buds  | payload 1 = on, 0 = off |
| 194 | SPATIAL_AUDIO_DATA      | buds->PC  | event 32 = quaternion (4x int16 LE / 10000) |
| 195 | SPATIAL_AUDIO_CONTROL   | both      | 0 attach, 1 detach, 4 keep-alive (every 2 s) |

Other IDs seen on connect: 96 (status), 104 (serial numbers), 205 (firmware version), 66 (acknowledgement).
