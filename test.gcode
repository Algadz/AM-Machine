;FLAVOR:RepRap
;Filament used: 0.329254m

M104 S210
M109 S210

;LAYER_COUNT:10
;LAYER:0
M107
G0 F4500 X-4.792 Y-.269 Z1

;TYPE:WALL-OUTER
G1 F2534.7 X-4.775 Y-.496 E0.03786
G1 X-4.741 Y-.746 E0.07981
G1 X-4.694 Y-1.004 E0.12343

;TYPE:SKIN
G1 F2534.7 X-2.118 Y4.104 E5.48257
G1 X-2.048 Y4.174
G0 F4500 X-1.195 Y4.461
