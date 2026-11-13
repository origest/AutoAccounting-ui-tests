"""Verify fixed manifest payload and extract exactly the two paired APKs, offline."""
import hashlib, io, json, pathlib, zipfile
HERE=pathlib.Path(__file__).resolve().parent
MANIFEST_HASH='7aaf3685616ca9d7071e35527bd253f7c6acadf7a7f5ac5a82fc201ac36af0fc'
def unpack(repo):
    raw=(HERE/'payload-manifest.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest()==MANIFEST_HASH, 'Manifest changed'
    m=json.loads(raw); pieces=[]
    assert 1 <= len(m['parts']) <= 16
    assert [p['path'] for p in m['parts']]==[f'payload.part{i:03d}' for i in range(len(m['parts']))]
    for part in m['parts']:
        path=repo/part['path']; assert path.is_file() and not path.is_symlink()
        content=path.read_bytes()
        assert len(content)==part['bytes'] and hashlib.sha256(content).hexdigest()==part['sha256']
        pieces.append(content)
    archive=b''.join(pieces)
    assert len(archive)==m['archive_bytes'] and hashlib.sha256(archive).hexdigest()==m['archive_sha256']
    out=HERE/'payload'; assert not out.exists(), 'Refuse overwrite'
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        assert sorted(z.namelist())==['app.apk','tests.apk'], 'Archive whitelist mismatch'
        verified={}
        for item in m['apks']:
            info=z.getinfo(item['path']); assert info.file_size==item['bytes']
            content=z.read(info)
            assert len(content)==item['bytes'] and hashlib.sha256(content).hexdigest()==item['sha256']
            verified[item['path']]=content
    out.mkdir()
    for name,content in verified.items(): (out/name).write_bytes(content)
    print('PAIR_VERIFIED')
if __name__=='__main__': unpack(HERE)


