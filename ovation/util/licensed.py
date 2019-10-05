"""
Utilities for working with github/licensed cached license data
"""

import pathlib
import yaml
import csv

from six import StringIO

_LICENSE_URLS = {'apache-2.0': 'https://www.apache.org/licenses/LICENSE-2.0',
                 'mit': 'https://opensource.org/licenses/MIT',
                 'gpl2': 'https://www.gnu.org/licenses/old-licenses/gpl-2.0.txt',
                 'gpl3': 'https://www.gnu.org/licenses/gpl-3.0.txt',
                 'gpl-3.0': 'https://www.gnu.org/licenses/gpl-3.0.txt',
                 'bsd-2-clause': 'https://opensource.org/licenses/BSD-2-Clause',
                 'bsd-3-clause': 'https://opensource.org/licenses/BSD-3-Clause',
                 'other': 'unknown'}
_LICENSE_NAMES = {'apache-2.0': 'Apache License Version 2.0',
                  'mit': 'MIT',
                  'gpl2': 'GNU General Public License Version 2',
                  'gpl3': 'GNU General Public License Version 3',
                  'gpl-3.0': 'GNU General Public License Version 3',
                  'bsd-2-clause': 'Simplified BSD License',
                  'bsd-3-clause': 'BSD License'}


def cached_license_dict(dep_path: pathlib.Path) -> dict:
    with dep_path.open('r') as f:
        dep = yaml.safe_load(f)
        dep['URL'] = _LICENSE_URLS.get(dep['license'], 'unknown')
        dep['license'] = _LICENSE_NAMES.get(dep['license'], dep['license'])
        return {(k.capitalize() if k is not "URL" else k): dep[k] for k in ['name', 'version', 'license', 'URL']}


def cached_licenses(cache_path: pathlib.Path) -> [dict]:
    return [cached_license_dict(p) for p in cache_path.glob("**/*.dep.yml")]


def cached_license_csv(cache_path: pathlib.Path, output: pathlib.Path = None) -> str:
    licenses = cached_licenses(cache_path)
    if output is None:
        with StringIO() as f:
            _write_licenses_csv(f, licenses)
            return f.getvalue()
    else:
        with output.open('w', newline='') as f:
            _write_licenses_csv(f, licenses)


def _write_licenses_csv(f, licenses):
    fieldnames = ['Name', 'Version', 'License', 'URL']
    writer = csv.DictWriter(f, fieldnames)
    writer.writeheader()
    writer.writerows(licenses)

