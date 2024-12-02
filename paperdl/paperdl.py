#!/usr/bin/env python3

"""Downloads specific version of PaperMC
according to provided spec."""

import hashlib
import logging
import pathlib as pth
import shutil
# FIXME: use 'requests' package instead
#        and proper TOML, not standard
import tomllib as toml
from urllib import request

DEFAULTS = {
    'spec': 'dlspec.toml',       # spec filename
}

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# TODO: make it used
class DLError(Exception):
    pass

def load_spec(filename):
    with open(filename, 'rb') as file:
        return toml.load(file)

def download(parsed_spec, entry_name, outdir):
    """
    Reads parsed spec (as returned by `load_spec`),
    reads url of the entry name (given as [myentry] in TOML),
    and downloads file from this url to outdir.
    """
    # ensure outdir is convertable to Path
    outdir = pth.Path(outdir)
    if not outdir.exists():
        log.info(f'Creating output directory "{outdir}"')
        outdir.mkdir()
    else:
        assert outdir.is_dir()

    entry = parsed_spec[entry_name]
    url = entry['url']
    log.debug(f'Parsed url for "{entry_name}":' +
              f' "{url}"')
    
    req = request.urlopen(url)      # open url as file-like
    fname = req.headers.get_filename()    # get filename as provided by server

    # don't trust the server filename
    # ensure fname is always a file, not some injection:
    # base = '/home/thd/server'
    # injection_response = '../../../../../../../../../etc/passwd'
    # result ->> /etc/passwd
    fname = pth.Path(fname).name    # will always be a filename

    # Check filename against format (if possible)
    fmt = entry.get('fname_fmt')
    log.debug(f'Fmt is "{fmt}"')
    if fmt:
        log.debug(f'Fmt result is "{fmt.format(**entry)}" <> "{str(fname)}"')
    
    if fmt and fmt.format(**entry) != str(fname):
        raise DLError('File format mismatch')


    # construct file path from two parts
    outname = outdir.joinpath(fname)
    log.debug(f'Constructed out filename "{outname}"')


    # finally download it
    with open(outname, 'wb') as outfile:
        # same as
        # outfile.write(req.read())
        shutil.copyfileobj(req, outfile)
        size = outfile.tell()       # returns bytes written
    
    hash = entry.get('hash')
    if hash and not verify_hash(hash, open(outname, 'rb')):
        raise DLError(f'Hash check failure. Expected {hash}')

    return size


def verify_hash(hashdescr, fileobj):
    # hash description takes form of
    # 'SHA256:ea8ac3f813abee88f3be3a7d3ae3d1b744542cbbd534bc427ed673f26a24e504'

    algo, hash_in = hashdescr.split(':', 1)

    algo = algo.lower()
    h = hashlib.file_digest(fileobj, algo)
    digest = h.hexdigest()
    log.debug(f'Computed hash: {digest}')

    return digest == hash_in


    



    

if __name__ == '__main__':
    log.setLevel(logging.DEBUG)
    spec = load_spec(DEFAULTS['spec'])
    log.debug(spec)

    ret = download(spec, 'papermc', './')
    log.debug(f'Downloaded {ret}')
