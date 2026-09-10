"""Behavioral fixtures: real pixels, alpha recovery, malformed manifests and CLI exits."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from extract_png_asset import extract
from audit_png_assets import audit
from generate_alpha_preview import generate
from validate_manifest import validate, asset_name
from create_example_assets import create


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.out=Path(self.temp.name)
    def tearDown(self): self.temp.cleanup()
    def shape(self,kind):
        im=Image.new('RGBA',(400,400)); d=ImageDraw.Draw(im)
        if kind=='circle': d.ellipse((64,64,335,335),fill=(30,150,100,255))
        else: d.rounded_rectangle((48,48,351,351),radius=64,fill=(30,150,100,255))
        p=self.out/(kind+'.png'); im.save(p); return p
    def test_circle_transparent_corners_and_density(self):
        source=self.shape('circle')
        for scale in (1,2,3,4):
            p=self.out/f'circle_{scale}.png'; extract(source,p,0,0,100,100,scale,4)
            report=audit(p); self.assertEqual(report['corner_alpha'],[0]*4)
            self.assertEqual(report['status'],'PASS')
            with Image.open(p) as image: self.assertEqual(image.size,(100*scale,)*2)
            self.assertEqual(len(generate(p,self.out/'qa')),4)
    def test_soft_shadow_unmatting_preserves_shadow(self):
        matte=Image.new('L',(160,160)); ImageDraw.Draw(matte).ellipse((40,44,120,124),fill=100)
        matte=matte.filter(ImageFilter.GaussianBlur(5))
        ImageDraw.Draw(matte).ellipse((44,36,116,108),fill=255)
        rgba=Image.new('RGBA',matte.size,(20,90,70)); rgba.putalpha(matte)
        flat=Image.alpha_composite(Image.new('RGBA',matte.size,'white'),rgba)
        src=self.out/'flat.png'; mask=self.out/'matte.png'; out=self.out/'clean.png'
        flat.save(src); matte.save(mask)
        extract(src,out,0,0,160,160,1,1,mask,'#ffffff')
        actual=np.asarray(Image.open(out)); expected=np.asarray(rgba)
        self.assertTrue(np.array_equal(actual[...,3],expected[...,3]))
        self.assertGreater(int(((actual[...,3]>0)&(actual[...,3]<255)).sum()),100)
        self.assertEqual(audit(out)['errors'],[])
        # Quantization may amplify RGB error at tiny alpha; composite must remain faithful.
        composite=np.asarray(Image.alpha_composite(Image.new('RGBA',rgba.size,'white'),Image.open(out))).astype(int)
        self.assertLessEqual(np.abs(composite-np.asarray(flat).astype(int)).max(),1)
    def test_rounded_rectangle(self):
        source=self.shape('rounded'); p=self.out/'rounded_2.png'
        extract(source,p,0,0,100,100,2,4)
        self.assertEqual(audit(p)['corner_alpha'],[0]*4); self.assertEqual(audit(p)['errors'],[])
    def test_opaque_background_allowed_but_transparent_rejected(self):
        p=self.out/'bg.png'; Image.new('RGBA',(80,80),'navy').save(p)
        self.assertEqual(audit(p,{'alphaRequired':False})['errors'],[])
        self.assertTrue(audit(p)['possible_background_rectangle']); self.assertTrue(audit(p)['errors'])
    def test_manifest_example_and_files(self):
        create(self.out)
        assets=json.loads((self.out/'Assets/UI/FigmaSync/figma_asset_manifest.json').read_text())
        ui=json.loads((self.out/'Assets/UI/FigmaSync/figma_ui_manifest.json').read_text())
        validate(assets,self.out); validate(ui,assets=assets)
        for a in assets['assets']: self.assertEqual(audit(self.out/a['unityPath'],a)['errors'],[])
        self.assertEqual(asset_name('export/btn/category_selected'),'btn_category_selected.png')
    def test_manifest_rejects_traversal_duplicates_bad_border(self):
        data=json.loads((ROOT/'examples/figma_asset_manifest.example.json').read_text())
        for mutation in ('path','duplicate','border','name','scale','extra'):
            d=copy.deepcopy(data); a=d['assets'][0]
            if mutation=='path': a['unityPath']='Assets/../icon_back.png'
            elif mutation=='duplicate': d['assets'].append(copy.deepcopy(a))
            elif mutation=='border': a.update(nineSlice=True,border=[20,0,20,0])
            elif mutation=='name': a['figmaName']='export/icon/back_copy'
            elif mutation=='scale': a['scaleFactor']=0
            else: a['unknownField']=True
            with self.assertRaises(ValueError,msg=mutation): validate(d)
    def test_ui_cycles_and_missing_assets(self):
        ui=json.loads((ROOT/'examples/figma_ui_manifest.example.json').read_text())
        ui['nodes'][0]['parentId']=ui['nodes'][0]['id']
        with self.assertRaises(ValueError): validate(ui)
        ui['nodes'][0]['parentId']=''
        with self.assertRaises(ValueError): validate(ui,assets={'assets':[]})
    def test_empty_rgb_clipping_and_fringe(self):
        p=self.out/'bad.png'; Image.new('RGBA',(40,40)).save(p); self.assertTrue(audit(p)['errors'])
        Image.new('RGB',(40,40),'white').save(p); self.assertFalse(audit(p)['rgba_mode'])
        im=Image.new('RGBA',(40,40)); ImageDraw.Draw(im).ellipse((0,5,30,35),fill='green'); im.save(p)
        self.assertTrue(audit(p)['touching_left_edge'])
        for color in ('white','black','blue','purple'):
            im=Image.new('RGBA',(40,40)); d=ImageDraw.Draw(im)
            from PIL import ImageColor
            d.ellipse((5,5,34,34),fill=ImageColor.getrgb(color)+(100,)); d.ellipse((10,10,29,29),fill=(0,180,80,255)); im.save(p)
            self.assertIn(color,audit(p)['fringe_candidates'])
    def test_bbox_invalid_and_mask_requirements(self):
        src=self.shape('circle')
        with self.assertRaises(ValueError): extract(src,self.out/'x.png',390,0,20,20)
        with self.assertRaises(ValueError): extract(src,self.out/'x.png',0,0,20,20,background='#ffffff')
    def test_cli_all_scripts(self):
        for f in (ROOT/'scripts').glob('*.py'):
            r=subprocess.run([sys.executable,str(f),'--help'],capture_output=True,text=True)
            self.assertEqual(r.returncode,0,f.name+r.stderr)
        p=self.shape('circle')
        result=subprocess.run([sys.executable,str(ROOT/'scripts/compare_images.py'),str(p),str(p),'--diff',str(self.out/'diff.png')],capture_output=True)
        self.assertEqual(result.returncode,0)
        q=self.out/'different.png'; Image.new('RGBA',(400,400),'red').save(q)
        result=subprocess.run([sys.executable,str(ROOT/'scripts/compare_images.py'),str(p),str(q)],capture_output=True)
        self.assertEqual(result.returncode,1)

    def test_cli_audit_and_bbox_outputs(self):
        create(self.out)
        manifest=self.out/'Assets/UI/FigmaSync/figma_asset_manifest.json'
        result=subprocess.run([sys.executable,str(ROOT/'scripts/audit_png_assets.py'),'--manifest',str(manifest),'--project-root',str(self.out),'--qa-dir',str(self.out/'qa')],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        records=json.loads(result.stdout)
        self.assertEqual(len(records),2)
        for record in records:
            self.assertTrue(all(Path(p).is_file() for p in record['previews']))
        source=self.out/'source.png'; Image.new('RGBA',(1080,1920),'white').save(source)
        target=self.out/'bbox.png'
        result=subprocess.run([sys.executable,str(ROOT/'scripts/preview_bboxes.py'),str(source),str(manifest),str(target)],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        with Image.open(target) as im: self.assertEqual(im.getpixel((56,80)),(255,0,0,255))

    def test_alpha_exception_requires_reason_and_size_checked(self):
        p=self.out/'edge.png'; im=Image.new('RGBA',(40,40)); ImageDraw.Draw(im).rectangle((0,10,20,30),fill='green'); im.save(p)
        policy={'alphaRequired':True,'alphaPolicy':{'allowedTouchingEdges':['left'],'reason':'Intentional source crop'}}
        self.assertEqual(audit(p,policy)['errors'],[])
        policy['alphaPolicy']['reason']=''
        self.assertTrue(audit(p,policy)['errors'])
        policy['sourceBounds']={'x':0,'y':0,'width':40,'height':40};policy['scaleFactor']=2
        self.assertFalse(audit(p,policy)['size_ok'])


if __name__=='__main__': unittest.main()
