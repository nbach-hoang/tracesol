"""Create a clean, reproducible project archive using Python's standard library."""
import hashlib
import json
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT.parent/'TraceSol_LaunchPad_2026_Complete.zip'


def include(path):
    rel=path.relative_to(ROOT)
    if any(p in {'.git','.venv','__pycache__','node_modules','dist','.idea'} for p in rel.parts):return False
    if path.suffix in {'.pyc','.log'} or path.name=='.env' or path.name.startswith('qa-'):return False
    if rel.as_posix().startswith('output/brief-render/'):return False
    return True


def main():
    files=sorted(p for p in ROOT.rglob('*') if p.is_file() and include(p) and p.name!='RELEASE_MANIFEST.json')
    manifest={'project':'TraceSol','version':'1.0.0','files':[{'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]}
    manifest_path=ROOT/'RELEASE_MANIFEST.json';manifest_path.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    with zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in [*files,manifest_path]:z.write(p,Path(ROOT.name)/p.relative_to(ROOT))
    with zipfile.ZipFile(OUT) as z:
        assert z.testzip() is None
    digest=hashlib.sha256(OUT.read_bytes()).hexdigest()
    OUT.with_suffix('.sha256').write_text(digest+'  '+OUT.name+'\n',encoding='ascii')
    print(json.dumps({'archive':str(OUT),'files':len(files)+1,'bytes':OUT.stat().st_size,'sha256':digest},indent=2))


if __name__=='__main__':main()
