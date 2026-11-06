# Run from the repository root with: yosys -c scripts/synth.tcl
yosys read_verilog -sv rtl/pll_control.sv
yosys hierarchy -check -top pll_control
yosys proc
yosys check -assert
yosys synth -top pll_control
yosys check -assert
yosys tee -o /tmp/pll-yosys-stat.json stat -json
set f [open /tmp/pll-yosys-stat.json r]
set report [read $f]
close $f
file delete /tmp/pll-yosys-stat.json
if {![regexp {"num_cells"\s*:\s*([0-9]+)} $report -> cells]} { error "No cell count in Yosys report" }
if {$cells < 1 || $cells > 1000} { error "Unexpected synthesized cell count: $cells" }
puts "Checked synthesized cell count: $cells"

# Also synthesize the actual firmware-controlled PLL and queue assembly.
yosys design -reset
yosys read_verilog -sv rtl/pll_control.sv rtl/sample_fifo.sv rtl/rv32_core.sv rtl/pll_soc.sv
yosys hierarchy -check -top pll_soc
yosys synth -top pll_soc
yosys check -assert
yosys stat
