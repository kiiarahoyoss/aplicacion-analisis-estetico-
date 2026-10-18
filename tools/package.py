"""Genera un HTML autónomo con estilos, código, imágenes y PDF incluidos."""
from pathlib import Path
import base64
import json
import re
import sys

root=Path(__file__).resolve().parents[1]
out=Path(sys.argv[1]) if len(sys.argv)>1 else root/'Derma.html'
html=(root/'index.html').read_text()
css=(root/'styles.css').read_text()
content=(root/'content.js').read_text()
app=(root/'app.js').read_text()
assets={str(p.relative_to(root)):base64.b64encode(p.read_bytes()).decode('ascii') for p in (root/'assets').rglob('*') if p.is_file()}
resolver='''
// Recursos incluidos: no requiere archivos adjuntos, servidor ni conexión.
const portableAssets = ASSETS_JSON;
const portableURLs = new Map();
function assetURL(path) {
  const [key, fragment] = path.split('#');
  if (!portableURLs.has(key)) {
    const encoded = portableAssets[key];
    if (!encoded) throw new Error('Recurso no incluido: '+key);
    const binary = atob(encoded);
    const bytes = new Uint8Array(binary.length);
    for (let i=0;i<binary.length;i++) bytes[i]=binary.charCodeAt(i);
    const type = key.endsWith('.pdf') ? 'application/pdf' : 'image/webp';
    portableURLs.set(key, URL.createObjectURL(new Blob([bytes], {type})));
  }
  return portableURLs.get(key) + (fragment ? '#'+fragment : '');
}
'''.replace('ASSETS_JSON',json.dumps(assets,separators=(',',':')))
app=re.sub(r'(src|href)="(assets/(?:docs|slides)/[^\"]+)"',lambda m:m[1]+'="${assetURL(`'+m[2]+'`)}"',app)
app=app.replace('.src=`assets/slides/${slideIndex}.webp`','.src=assetURL(`assets/slides/${slideIndex}.webp`)')
html=html.replace('<link rel="stylesheet" href="styles.css">','<style>'+css+'</style>')
html=html.replace('<script src="content.js" defer></script><script src="app.js" defer></script>','')
# Los scripts se ejecutan al final, cuando la interfaz ya existe.
def script(text):
 return '<script>'+re.sub(r'</script',r'<\\/script',text,flags=re.I)+'</script>'
html=html.replace('</body>', '<noscript><p>Esta aplicación necesita JavaScript. Descarga el archivo HTML y ábrelo en Chrome, Edge, Firefox o Safari; la vista previa de archivos puede no ejecutarlo.</p></noscript>'+script(content)+script(resolver)+script(app)+'</body>')
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(html)
print(f'HTML autónomo: {out} ({out.stat().st_size:,} bytes; {len(assets)} recursos incluidos)')
