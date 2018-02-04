#!/usr/bin/env python3
#
# Copyright (C) 2018  The Victims Project
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import hashlib
import json
import logging
import os
import shutil
import tempfile
import zipfile

from aiohttp import web

#: Application instance
APP = web.Application()
#: Shortcut for a bad http request
BAD_REQUEST = web.Response(status=400, text='{"error": "bad request"}')
#: Shortcut for an OK http request
OK = web.Response(status=200)

#: All supported upload file types
SUPPORTED_FILE_TYPES = (
    '.whl',
    '.egg',
    '.zip',
)
#: All hashable file types
HASHABLE_FILE_TYPES = (
    '.pyc',
    '.pyo',
    '.py',
)


async def handle_health(request):
    """
    Simple health endpoint.
    """
    return OK


async def handle_hash(request):
    """
    Handle a request to hash a Python package.
    """
    write_to = tempfile.mkdtemp()
    print(write_to)
    try:
        APP.logger.info('Writing to %s', write_to)
        package_path = os.path.sep.join([write_to, 'package'])
        with open(package_path, 'wb+') as out_fobj:
            package = await request.post()
            lib = package.get('library2')
            if not lib:
                print('Nothing in library2 form element')
                return BAD_REQUEST
            out_fobj.write(lib.file.read())

        # Must be a supported file type
        supported = map(
            lambda r: lib.filename.endswith(r), SUPPORTED_FILE_TYPES)
        if True not in supported:
            print('Bad file type passed in')
            return BAD_REQUEST

        extract_package(write_to)
        version = find_version(write_to)

        data = json.dumps({
            'hash': hash_file(package_path),
            'name': lib.filename,
            'verison': version,
            'files': hash_contents(write_to),
            })

        return web.Response(text=data, content_type='application/json')
    finally:
        shutil.rmtree(write_to)


def hash_file(path):
    """
    Shortcut to properly hash a file.
    """
    with open(path, 'rb') as hf:
        return hashlib.sha512(hf.read()).hexdigest()


def extract_package(path):
    """
    Extracts a python zip based package to a standard location.
    """
    extract_path = os.path.sep.join([path, '_extraction'])
    package_path = os.path.sep.join([path, 'package'])
    os.mkdir(extract_path)
    zf = zipfile.ZipFile(package_path, 'r')
    zf.extractall(extract_path)
    zf.close()


def find_version(path):
    """
    Reads one of two possible files to get the version/
    """
    for root, dirs, files in os.walk(path):
        for file in files:
            if file == 'metadata.json':
                with open(os.path.sep.join([root, file])) as f:
                    mf = json.load(f)
                    return mf['version']
            elif file == 'PKG-INFO':
                with open(os.path.sep.join([root, file])) as f:
                    for line in f.readlines():
                        if line.startswith('Version'):
                            return line[9:-1]
                            break
    # This shouldn't happen, but just in case ...
    return 0


def hash_contents(path):
    """
    Hashes the contents of all py/pyc/pyo files in a directory.
    """
    contents = []
    top_dir = os.path.sep.join([path, '_extraction'])
    for root, dirs, files in os.walk(top_dir):
        for file in files:
            hashable = map(
                lambda r: file.endswith(r), HASHABLE_FILE_TYPES)
            if True in hashable:
                full_path = os.path.sep.join([root, file])
                contents.append({
                    'name': full_path,
                    'hash': hash_file(full_path),
                })
    return contents


if __name__ == '__main__':
    APP.router.add_get('/healthz', handle_health)
    APP.router.add_post('/hash', handle_hash)

    web.run_app(APP, host="0.0.0.0", port=8080)
