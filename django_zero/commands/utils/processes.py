import os
import shlex
import subprocess

from django_zero.config import features
from django_zero.utils import get_env

DEFAULT_DEV_PROCESSES = [
    'server',
    'assets',
]


def get_procs(mode='dev'):
    procs = {}
    if mode == 'dev':
        procs['server'] = 'python -m django_zero manage runserver'
        procs['assets'] = 'python -m django_zero webpack --watch --colors'
    elif mode == 'prod':
        procs['server'] = 'python -m django_zero gunicorn --access-logfile -'
    else:
        raise NotImplementedError('Unknown mode {}.'.format(mode))

    if features.is_celery_enabled():
        procs['beat'] = 'python -m django_zero celery beat'
        procs['worker'] = 'python -m django_zero celery worker'

    return procs

def create_honcho_manager(*, printer=None, mode='dev', **kwargs):
    environ = {
        **os.environ,
        **kwargs.pop('environ', {}),
        'PYTHONUNBUFFERED': '1',
    }

    from honcho.manager import Manager
    m = Manager(printer=printer)

    for proc_name, proc_cmd in sorted(get_procs(mode).items()):
        m.add_process(proc_name, proc_cmd, env=environ)

    return m


def call_manage(*args, environ=None):
    return subprocess.call(
        'python -m django_zero manage ' + ' '.join(map(shlex.quote, args)),
        env={**os.environ, **get_env(), **(environ or {})},
        shell=True,
        )


def call_webpack(*args, environ=None):
    return subprocess.call(
        'yarn run webpack --config config/webpack.js ' + ' '.join(map(shlex.quote, args)),
        env={**os.environ, **get_env(), **(environ or {})},
        shell=True,
    )