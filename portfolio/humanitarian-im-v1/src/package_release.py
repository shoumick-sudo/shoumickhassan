import hashlib,json,zipfile
from pathlib import Path
root=Path(__file__).resolve().parents[1]
files=[p for p in sorted(root.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and not p.name.endswith('.inspect.ndjson') and p.name!='MANIFEST.sha256']
(root/'MANIFEST.sha256').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(root).as_posix()+'\n' for p in files))
archive=root.parent/'Humanitarian_IM_Demonstrator_v0_1.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for p in files+[root/'MANIFEST.sha256']:z.write(p,'humanitarian-im-v0.1.0/'+p.relative_to(root).as_posix())
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for line in (root/'MANIFEST.sha256').read_text().splitlines():
        digest,name=line.split('  ',1);assert hashlib.sha256(z.read('humanitarian-im-v0.1.0/'+name)).hexdigest()==digest
print(json.dumps({'archive':str(archive),'files':len(files)+1,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'checksums':'passed'}))
