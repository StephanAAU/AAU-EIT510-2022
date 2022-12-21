<QucsStudio Schematic 4.3.1>
<Properties>
View=-30,-10,1436,611,0.987324,45,0
Grid=10,10,1
DataSet=*.dat
DataDisplay=
OpenDisplay=1
showFrame=0
FrameText0=Title
FrameText1=Drawn By:
FrameText2=Date:
FrameText3=Revision:
</Properties>
<Symbol>
</Symbol>
<Components>
GND * 1 300 210 0 0 0 0
SPfile X1 1 300 160 -26 -59 0 0 "C:/Users/A/Aalborg Universitet/EIT4 - 410 - AAUSAT PROJECT - General/EIT5/Projekt/optimizing_pi/optimizing_pi/Test_of_pi_match_calc/Ant3Proto.s1p" 1 "1" 0 "polar" 0 "linear" 0 "short" 0 "none" 0 "block" 0 "SOT23" 0
Pac P1 1 40 200 18 -26 0 0 "1" 1 "50 Ω" 1 "0 dBm" 0 "1 GHz" 0 "26.85" 0 "SUBCLICK" 0
GND * 1 40 230 0 0 0 0
.SP SP1 1 80 290 0 65 0 0 "log" 1 "600MHz" 1 "1GHz" 1 "1001" 1 "no" 0 "1" 0 "2" 0 "none" 0
GND * 1 220 240 0 0 0 0
C C1 1 220 210 17 -26 0 1 "5 pF" 1 "0" 0 "" 0 "neutral" 0 "SMD0603" 0
L L1 1 170 160 -26 10 0 0 "3.3 nH" 1 "0" 0 "" 0 "SELF-WE-PD3S" 0
GND * 1 110 220 0 0 0 0
C C2 1 110 190 17 -26 0 1 "20 pF" 1 "0" 0 "" 0 "neutral" 0 "SMD0603" 0
</Components>
<Wires>
300 190 300 210 "" 0 0 0 ""
30 220 40 220 "" 0 0 0 ""
40 220 40 230 "" 0 0 0 ""
220 160 270 160 "" 0 0 0 ""
220 160 220 180 "" 0 0 0 ""
200 160 220 160 "" 0 0 0 ""
40 160 40 170 "" 0 0 0 ""
40 160 110 160 "" 0 0 0 ""
110 160 140 160 "" 0 0 0 ""
</Wires>
<Diagrams>
<Rect 600 250 360 220 31 #c0c0c0 1 00 1 6e+08 5e+07 1e+09 1 -22.5811 10 2.00921 1 0 0 0 315 0 225 "frequency" "" "">
	<Legend 10 -100 0>
	<"dB(S[1,1])" "" #0000ff 0 3 0 0 0 0 "">
	<"dB(S[2,1])" "" #ff0000 0 3 0 0 0 0 "">
	<"dB(S[2,2])" "" #ff00ff 0 3 0 1 0 0 "">
	<"wphase(S[2,1])" "" #000000 0 3 0 0 1 0 "">
</Rect>
<Smith 600 550 220 220 31 #c0c0c0 1 00 1 0 1 1 1 0 4 1 1 0 4 1 315 0 225 "" "" "">
	<Legend 10 -100 0>
	<"S[1,1]" "" #0000ff 0 3 0 0 0 0 "">
</Smith>
</Diagrams>
<Paintings>
</Paintings>
