# 在django完美嵌入noVNC
    前置条件
    Django==3.2.2
    numpy==1.20.3
    redis==3.5.3
    simplejson==3.17.2
    uuid==1.30
    目标服务器需要安装vnc server
## 1. 对noVNC进行项目适配，主要是js的静态路径和websocket请求path
### 修改vnc.html
```html
    <script>
        var token = "{{token}}";
    </script>
```
传入token以便于websockify转发
### 修改ui.js
```js
        url += '://' + host;
        if (port) {
            url += ':' + port;
        }
        url += '/' + path;
        url += '/?token=' + token # 加上这句
```
## 2. 拉取websockify官方包进行修改
[websockify github](https://github.com/novnc/websockify)
### 主要修改token_plugins.py文件
可以自行定义一个新的类，只需要在websockify启动时接入即可
```python
class TokenRedis(object):
    def __init__(self, src):
        self._server, self._port, self._password = src.split(":")

    def lookup(self, token):
        try:
            import redis
            import simplejson
        except ImportError as e:
            print("package redis or simplejson not found, are you sure you've installed them correctly?",
                  file=sys.stderr)
            return None

        client = redis.Redis(host=self._server, port=self._port, password=self._password or None)
        stuff = client.get(token)
        if stuff is None:
            return None
        else:
            combo = simplejson.loads(stuff.decode("utf-8"))
            pair = combo["host"]
            return pair.split(':')
```
## 3. 适配django
### 在wsgi中启动，也可以单独拎出去启动
```python
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
```
### 添加url
```python
    path(r'api/vnc', views.run_vnc),
    re_path('^static/(?P<path>.*)', serve, {'document_root': settings.STATIC_URL}),
```
### 添加view 生成token可以放在你项目的其他逻辑中，前端只需要window.open('base_url/?token=token')即可
```python 
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
```
### 启动项目即可访问
