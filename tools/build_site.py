"""Prepara el sitio para GitHub Pages, con HTML y ZIP descargables."""
from pathlib import Path
import importlib.util
import runpy
import shutil
import sys
import zipfile

root=Path(__file__).resolve().parents[1]
site=root/'_site'
site.mkdir(exist_ok=True)
(site/'downloads').mkdir(exist_ok=True)
for name in ['index.html','styles.css','app.js','content.js']:
 shutil.copy2(root/name,site/name)
shutil.copytree(root/'assets',site/'assets',dirs_exist_ok=True)
# La versión compartida tiene un enlace de descarga real, relativo a la web.
html=(site/'index.html').read_text()
banner='<div class="download-banner"><span>También puedes usarla sin conexión.</span><a class="btn secondary" href="downloads/Derma.zip" download>Descargar aplicación ZIP</a></div>'
html=html.replace('</header>','</header>'+banner,1)
html=html.replace('</head>','<style>.download-banner{display:flex;justify-content:space-between;align-items:center;gap:15px;margin:18px 28px 0;padding:13px 18px;border:1px solid #e8e5e0;border-radius:12px;background:white;font-size:11px;color:#767580}@media(max-width:540px){.download-banner{margin:15px 20px 0;flex-direction:column;align-items:stretch;text-align:center}.download-banner .btn{font-size:11px}}</style></head>')
(site/'index.html').write_text(html)
original_argv=sys.argv
sys.argv=['package.py',str(site/'downloads/Derma.html')]
try:runpy.run_path(str(root/'tools/package.py'),run_name='__main__')
finally:sys.argv=original_argv
zip_path=site/'downloads/Derma.zip'
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
 z.write(site/'downloads/Derma.html','Derma.html')
 z.writestr('LEEME.txt','Descomprime el archivo y abre Derma.html con un navegador. Incluye estudio, examen, imagenes y los PDF. No requiere instalacion.\n')
with zipfile.ZipFile(zip_path) as z:
 assert z.testzip() is None
 assert z.getinfo('Derma.html').file_size==(site/'downloads/Derma.html').stat().st_size
assert 'href="downloads/Derma.zip"' in (site/'index.html').read_text()
print('Sitio listo en _site; ZIP verificado y enlazado. No se ha publicado.')
