"""
WSGI config for djangoNoVNC project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os
from multiprocessing.dummy import Process

from django.conf import settings
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoNoVNC.settings.dev')

application = get_wsgi_application()


def worker():
    '''
        Multi process service VNC start
    '''
    websockify_path = settings.BASE_DIR / 'novnc/websockify/run'
    web_path = settings.BASE_DIR / 'static/novnc'
    cert_path = settings.BASE_DIR / 'novnc/websockify/novnc.pem'
    redis_path = settings.VNC_TOKEN_SOURCE
    port = settings.VNC_PROXY_PORT

    # cmd = u'%s -v --web %s --cert %s --token-plugin TokenRedis --token-source %s %s' % (
    #     websockify_path, web_path, cert_path, redis_path, port)
    cmd = u'%s -v --web %s --token-plugin TokenRedis --token-source %s %s' % (
        websockify_path, web_path, redis_path, port)
    print(cmd)
    os.system(cmd)


def start_websockify():
    print('start vnc proxy..')

    t = Process(target=worker, args=())
    t.start()

    print('vnc proxy started..')


start_websockify()
