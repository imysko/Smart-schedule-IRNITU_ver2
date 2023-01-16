import datetime
import os
import zipfile
from tempfile import NamedTemporaryFile

from db.sqlite_generator import sqlite_generate

fp = NamedTemporaryFile(delete=False)
try:
    sqlite_generate(fp.name)

    pth = os.path.abspath("./sqlite_backups")
    os.makedirs(pth, exist_ok=True)
    fp.close()

    filename = os.path.join(pth, f"sqlite_{datetime.datetime.now():%Y%m%d%H}.db.zip")
    with zipfile.ZipFile(filename, 'w', compresslevel=9, compression=zipfile.ZIP_BZIP2) as zf:
        zf.write(fp.name, "test.db")

    os.unlink("sqlite.db.zip")
    os.symlink(filename, "sqlite.db.zip")
finally:
    os.unlink(fp.name)
