"""Regression tests for visible damage hidden by global averages and permissive QA."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from compare_images import compare


class FidelityTests(unittest.TestCase):
    def test_small_replaced_icon_fails_local_gate(self):
        source = Image.new('RGBA', (1000,1000), 'white')
        actual = source.copy()
        ImageDraw.Draw(actual).rectangle((20,20,29,29), fill='blue')
        global_result, _ = compare(source, actual, 8, .01)
        self.assertTrue(global_result['numerical_pass'])
        local_result, _ = compare(source, actual, 8, .01,
            [{'name':'icon','x':20,'y':20,'width':10,'height':10}])
        self.assertFalse(local_result['numerical_pass'])

    def test_exact_rejects_single_pixel(self):
        source = Image.new('RGBA',(64,64),'white'); actual = source.copy()
        actual.putpixel((20,20),(254,255,255,255))
        self.assertFalse(compare(source,actual)[0]['numerical_pass'])
        self.assertTrue(compare(source,source)[0]['numerical_pass'])

    def test_missing_highlight_and_changed_alpha_fail(self):
        source = Image.new('RGBA',(64,64)); ImageDraw.Draw(source).ellipse((8,8,55,55),fill='white')
        actual = source.copy(); actual.putpixel((32,32),(255,255,255,0))
        self.assertFalse(compare(source,actual)[0]['numerical_pass'])

    def test_hidden_rgb_is_ignored(self):
        a = Image.new('RGBA',(8,8),(255,0,0,0)); b=Image.new('RGBA',(8,8),(0,255,0,0))
        self.assertTrue(compare(a,b)[0]['numerical_pass'])

    def test_size_and_regions_are_strict(self):
        a=Image.new('RGBA',(64,64),'white')
        self.assertFalse(compare(a,Image.new('RGBA',(32,64)))[0]['numerical_pass'])
        for bounds in ((60,0,8,8),(-1,0,8,8),(0,0,0,8),(0.5,0,8,8)):
            with self.assertRaises(ValueError):
                compare(a,a,regions=[dict(zip(('name','x','y','width','height'),('test',*bounds)))])

    def test_cli_forbids_vacuous_gate_and_writes_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp); a=folder/'a.png'; b=folder/'b.png'
            Image.new('RGBA',(20,20),'white').save(a); Image.new('RGBA',(20,20),'black').save(b)
            cmd=[sys.executable,str(ROOT/'scripts/compare_images.py'),str(a),str(b)]
            for flags in (['--max-changed-ratio','1'],['--threshold','255'],['--exact','--threshold','8']):
                self.assertEqual(subprocess.run(cmd+flags,capture_output=True).returncode,2)
            regions=folder/'regions.json'
            regions.write_text(json.dumps([{'name':'icon','x':0,'y':0,'width':10,'height':10}]))
            report=folder/'report.json'
            result=subprocess.run(cmd+['--exact','--regions',str(regions),'--report',str(report),
                '--overlay',str(folder/'overlay.png'),'--diff',str(folder/'diff.png')],capture_output=True)
            self.assertEqual(result.returncode,1)
            self.assertEqual(json.loads(report.read_text())['status'],'FAIL')
            self.assertTrue((folder/'regions/000_actual.png').exists())
            self.assertTrue((folder/'overlay.png').exists())
            result=subprocess.run(cmd+['--measure-only'],capture_output=True,text=True)
            self.assertEqual(result.returncode,0)
            self.assertIsNone(json.loads(result.stdout)['numerical_pass'])
            self.assertEqual(json.loads(result.stdout)['status'],'MEASURED')


if __name__ == '__main__': unittest.main()
