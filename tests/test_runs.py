import os
import shutil
import tempfile
import unittest

from tradssat import DSSATRun, set_dssat_dir, ExpFile
from tradssat.exper.exper_vars import TRT_HEAD

_test_vars = {
    'SOL': 'SRGF',
    'WTH': 'SRAD',
    'EXP': 'FACD',
    'CUL': 'P1',
    'ECO': 'TOPT',
}


class TestRuns(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()

        mock_dir = shutil.copytree('rsrc/mock_DSSAT', os.path.join(cls.temp_dir.name, 'DSSAT47'))
        set_dssat_dir(mock_dir)
        cls.file = 'rsrc/mock_DSSAT/Exper/Maize/BRPI0202.MZX'

        cls.dssat_run = DSSATRun(cls.file)
        cls.ref_expfile = ExpFile(cls.file)

    def _get_run(self):
        return DSSATRun(self.file)

    def test_get_general_val(self):
        val = self.dssat_run.get_general_val('PEOPLE')
        ref_val = self.ref_expfile.get_value('PEOPLE')

        self.assertEqual(val, ref_val)

    def test_set_general_val(self):
        run = self._get_run()
        run.set_general_val('PEOPLE', 'me')
        new_val = run.get_general_val('PEOPLE')
        self.assertEqual(new_val, 'me')

    def test_n_factor_levels(self):
        ref_n = self.ref_expfile.get_value('INGENO').size

        n = self.dssat_run.n_factor_levels('CULTIVARS')
        self.assertEqual(n, ref_n)

    def test_get_trt_num(self):
        ref_names = self.ref_expfile.get_value('TNAME')
        ref_i_s = self.ref_expfile.get_value('N', sect=TRT_HEAD)

        ref_i = 4
        name = ref_names[ref_i_s == ref_i]
        i = self.dssat_run.get_trt_num(name)

        self.assertEqual(ref_i, i)

    def test_get_trt_name(self):
        ref_names = self.ref_expfile.get_value('TNAME')
        ref_i = self.ref_expfile.get_value('N', sect=TRT_HEAD)

        i = 2
        name = self.dssat_run.get_trt_name(i)

        self.assertEqual(ref_names[ref_i == i], name)

    def test_get_trt_val(self):

        for subfile, vr in _test_vars.items():
            with self.subTest(file=subfile):
                self.dssat_run.get_trt_val(vr, trt=1)

    def test_set_trt_val(self):
        run = self._get_run()

        trt = 5
        val = 15
        run.set_trt_val('IDEP', val, trt=trt)

        new_val = run.get_trt_val('IDEP', trt)

        self.assertEqual(val, new_val)

    def test_add_treatment(self):
        run = self._get_run()
        name = 'Test treatment'

        run.add_treatment(name)

        trts = run.treatments(name=True)
        self.assertIn(name, trts)

    def test_remove_treatment(self):
        run = self._get_run()

        i = 3
        trts = run.treatments(name=True).tolist()
        name = trts.pop(i)

        run.remove_treatment(name)

        new_trts = run.treatments(name=True).tolist()
        self.assertLessEqual(new_trts, trts)

    def test_add_factor_level(self):
        run = self._get_run()

        n_levels = run.n_factor_levels('SA')
        vals = {'SADAT': 2073, 'SANAME': 'New level', 'SABL': 30}
        run.add_factor_level('SA', vals=vals)

        for vr, vl in vals.items():
            self.assertEqual(run.get_factor_level_val(vr, n_levels + 1), vl)

    def test_get_trt_factor_level(self):

        factor = 'CU'
        trt = 5

        factors = self.ref_expfile.get_value(factor)
        trts = self.ref_expfile.get_value('N', sect=TRT_HEAD)

        ref = factors[trts == trt][0]

        val = self.dssat_run.get_trt_factor_level(trt, 'CU')
        self.assertEqual(val, ref)

    def test_set_trt_factor_level(self):
        run = self._get_run()

        new_level = 2
        trt = 1
        run.set_trt_factor_level(trt=trt, factor='CU', level=new_level)

        ref_val = run.get_factor_level_val('INGENO', new_level)
        new_val = run.get_trt_val('INGENO', trt)

        self.assertEqual(ref_val, new_val)

    def test_get_factor_level_val(self):
        for subfile, vr in _test_vars.items():
            with self.subTest(file=subfile):
                self.dssat_run.get_factor_level_val(vr, level=1)

    @unittest.skip('not ready')
    def test_set_factor_level_val(self):
        pass

    @unittest.skip('not ready')
    def test_clean(self):
        pass

    @unittest.skip('not ready')
    def test_check(self):
        pass

    @unittest.skip('not ready')
    def test_write(self):
        pass

    @unittest.skip('not ready')
    def test_write_overwrite(self):
        pass

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()
