import os
import pytest
import pyansys

test_path = os.path.dirname(os.path.abspath(__file__))
testfiles_path = os.path.join(test_path, 'testfiles')


@pytest.mark.skipif(os.name == 'nt', reason='Requires multiple instances')
def test_convert(tmpdir):
    vm_file = os.path.join(testfiles_path, 'vm1.dat')
    pyscript = str(tmpdir.mkdir('tmpdir').join('vm1.py'))
    clines = pyansys.convert_script(vm_file, pyscript, loglevel='ERROR')
    assert len(clines)

    if pyansys.has_ansys:
        exec(open(pyscript).read())


def test_convert_no_use_function_names(tmpdir):
    vm_file = os.path.join(testfiles_path, 'vm1.dat')
    pyscript = str(tmpdir.mkdir('tmpdir').join('vm1.py'))
    clines = pyansys.convert_script(vm_file, pyscript, loglevel='ERROR',
                                    use_function_names=False)
