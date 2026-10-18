#!/usr/bin/env python3
"""Responsive smoke test against a static server; screenshots for editorial review."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
out=root/'qa/screens'
out.mkdir(parents=True,exist_ok=True)
base="http://127.0.0.1:8000/DKKICI/"
urls=['','pl/','profile/','pl/profil/','leadership/','pl/organizacje/','media/','pl/media/','gallery/','pl/galeria/','publications/','pl/publikacje/']
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
 failures=[]
 for width,height,mode in ((390,844,'mobile'),(1440,900,'desktop')):
  page=browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1)
  page.on('pageerror',lambda ex:failures.append('JS exception: '+str(ex)))
  for name in urls:
   result=page.goto(base+name,wait_until='domcontentloaded',timeout=30000)
   page.wait_for_timeout(380)
   if not result or result.status>=400:failures.append(f'HTTP {name}: {result.status if result else None}')
   overflow=page.evaluate('Math.max(document.documentElement.scrollWidth, document.body.scrollWidth) - window.innerWidth')
   if overflow>4:
    bad=page.evaluate("""() => Array.from(document.querySelectorAll('*')).map(el=>({el,rect:el.getBoundingClientRect()})).filter(x=>x.rect.right>innerWidth+4 || x.rect.left < -4).slice(0,30).map(x=>({tag:x.el.tagName,cls:x.el.className?.toString().slice(0,70),txt:x.el.textContent.slice(0,70),left:Math.round(x.rect.left),right:Math.round(x.rect.right)}))""")
    print('OFFENDERS',mode,name,bad)
    failures.append(f'Horizontal overflow {mode} {name}: {overflow}px')
   if name in ('','pl/','profile/','pl/profil/','media/','gallery/','leadership/'):
    filename=(name.strip('/').replace('/','-') or 'home')
    page.screenshot(path=str(out/(mode+'-'+filename+'.jpg')),type='jpeg',quality=70)
   print(mode,name,result.status if result else 'none','overflow=',overflow)
  if mode=='mobile':
   page.goto(base+'gallery/',wait_until='domcontentloaded')
   assert page.locator('[data-gallery-item]').count()==26
   page.locator('[data-gallery-filter="media"]').click()
   assert page.locator('[data-gallery-item]:visible').count()>=12
   page.locator('[data-gallery-filter="all"]').click()
   page.locator('[data-gallery-open]').first.click()
   assert page.locator('#photo-viewer').evaluate('(el)=>el.open')
   page.keyboard.press('Escape')
   assert not page.locator('#photo-viewer').evaluate('(el)=>el.open')
   page.goto(base+'profile/',wait_until='domcontentloaded')
   assert page.locator('a[href="../publications/"]').count()>=1
   assert page.locator('text=PACFA Clinical Registrant').count()>=1
   page.goto(base+'publications/',wait_until='domcontentloaded')
   page.locator('.publication-tile').first.click()
   assert page.locator('#publication-dialog').evaluate('(el)=>el.open')
  page.close()
 browser.close()
 if failures:
  print('\n'.join(failures))
  raise RuntimeError(str(len(failures))+' QA failures')
 print('PASS: responsive layout, routes and gallery interactions')
