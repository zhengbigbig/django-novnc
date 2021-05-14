
import redis
import simplejson
from django.shortcuts import render
from django.conf import settings


# Create your views here.


def run_vnc(request):
    if request.method == 'GET':
        '''
            Call the VNC proxy for remote control
        '''
        view_only = request.GET.get('view_only', 'false')  # False can control the or true can only view

        # The proxy server IP and port, this usually use school server LAN IP (127.0.0.1, 6080 is the default port)
        token = request.GET.get('token')
        host = request.get_host().split(':')[0]
        port = request.get_host().split(':')[1]
        content = {
            "host": host, "port": port, "token": token, "view_only": view_only, "path": '?' + token
        }
        return render(request, 'novnc/vnc.html', content, content_type="text/html;charset=utf-8")
    else:
        token = ''.join(str(uuid.uuid4()).split('-'))
        redis_source = settings.VNC_TOKEN_SOURCE.split(":")
        client = redis.Redis(host=redis_source[0], port=redis_source[1], db=0, password=redis_source[2] or None)
        # host port 是安装vncserver的服务器
        client.set(token, simplejson.dumps({"host": "192.168.5.120" + ":" + "5900"}),
                   60 * 60 * 24)
