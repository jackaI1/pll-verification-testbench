import subprocess

import pytest
from scripts.riscv_suite import build_core
from rv_reference import program, reference


@pytest.fixture(scope='module', params=[0,1], ids=['ripple-baseline','carry-select'])
def core(request, tmp_path_factory):
    return build_core(tmp_path_factory.mktemp(f'core-{request.param}'), request.param)


@pytest.mark.parametrize('seed', [17,409,20261106])
def test_core_against_sequential_model(core, tmp_path, seed):
    image = program(seed)
    binary, trace = tmp_path/'program.bin', tmp_path/'retire.trace'
    binary.write_bytes(image)
    proc = subprocess.run([str(core), str(binary), str(trace)], text=True, capture_output=True, timeout=30)
    assert proc.returncode == 0, proc.stdout+proc.stderr
    actual = [tuple(int(v,16) for v in line.split()) for line in trace.read_text().splitlines()]
    expected = list(reference(image))
    assert len(actual)==len(expected)
    for got, want in zip(actual, expected):
        assert got[:3] == want[:3], f'retirement mismatch: {got} != {want}'
        if want[3] is not None: assert got[3]==want[3], f'register data mismatch: {got} != {want}'
    for event in ['stalls','flushes','forwards']:
        assert int(proc.stdout.split(event+'=')[1].split()[0])>0, proc.stdout
