import hashlib,zipfile
from pathlib import Path
root=Path(__file__).resolve().parents[1]
files=[p for p in sorted(root.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and not p.name.endswith('.inspect.ndjson') and p.name!='MANIFEST.sha256']
(root/'MANIFEST.sha256').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(root))+'\n' for p in files))
out=root.parent/'STP_Monitoring_Reconstruction_v1.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
    for p in files+[root/'MANIFEST.sha256']:z.write(p,'stp-monitoring-reconstruction/'+str(p.relative_to(root)))
with zipfile.ZipFile(out) as z:
    assert z.testzip() is None
    for line in (root/'MANIFEST.sha256').read_text().splitlines():
        h,p=line.split('  ',1);assert hashlib.sha256(z.read('stp-monitoring-reconstruction/'+p)).hexdigest()==h
print(str(out));print('Archive integrity and all enclosed SHA-256 checks passed.')
