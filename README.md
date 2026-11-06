# Digital PLL verification testbench

I built a digital PLL control block because I wanted a practical way to check how a clock controller responds when its reference and feedback signals drift apart. A phase-locked loop (PLL) tries to keep a feedback signal aligned with a reference. This project models its digital decision-making and checks that the decisions stay consistent across many input patterns.

The block counts clock cycles to make a divided feedback pulse, compares it with the reference pulse, and adjusts a small control counter. It reports lock after four aligned pulses and drops lock when the pulses disagree. A Python testbench drives inputs, watches outputs and compares each cycle with an independent model. I also run the same test against an intentionally faulty divider to show that the checker catches a real error.

## Try it

Install Python 3.10 or newer, Verilator 5.036 or newer, Yosys and a C++ compiler. On macOS with Homebrew:

```sh
brew install verilator yosys
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q
yosys -c scripts/synth.tcl
```

The two pytest cases run the correct design and the injected fault. The fault case passes only when the scoreboard identifies the expected divider mismatch. The Tcl script synthesizes the circuit, checks for structural problems and rejects an empty or unexpectedly large cell count.

## How it works

`rtl/pll_control.sv` contains the synchronous phase-frequency comparison, saturating loop-filter counter, divider and lock detector. The divider accepts ratios from 2 to 15; inputs below 2 use 2. Reset before changing the ratio. A feedback pulse occurs once per ratio clock cycles. Four consecutive coincident reference and feedback pulses assert lock; any unmatched pulse clears it.

The pyuvm environment in `tests/pll_env.py` has a driver, monitor and scoreboard. Its cycle-by-cycle Python reference model checks the feedback pulse, phase decisions, control count and lock state. A fixed random seed makes the constrained input patterns repeatable. Coverage bins require ratios 2 through 8, both phase-error directions, no error and lock. Directed checks exercise lock acquisition and loss. `INJECT_BUG` changes the divider terminal count only in the fault build.

This is a digital control model, not a complete physical PLL: it does not model an analog oscillator, jitter or frequency response, and the control counter does not feed back into a physical clock. Both the reference and feedback are sampled on the same clock.

## Automated checks

GitHub Actions runs both simulation cases and the Tcl-driven Yosys synthesis and structural check on every push and pull request. The simulation requires all 11 functional coverage bins; the synthesis script checks that the mapped design has between 1 and 1000 cells.
