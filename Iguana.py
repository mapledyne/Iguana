import requests
import json

class Channel(object):
    name = ''

class Version(object):
    major = 0
    minor = 0
    build = 0
    ext = 0
    def __init__(self, major, minor, build, ext=0):
        super(Version, self).__init__()
        self.major = major
        self.minor = minor
        self.build = build
        if len(ext) > 0:
            self.ext = ext

    def __str__(self):
        ver = str(self.major) + '.' + str(self.minor) + '.' + str(self.build)
        if self.ext > 0:
            ver += '.' + str(self.ext)
        return ver

class Iguana(object):
    url_base = 'http://localhost:6543/'
    user = 'admin'
    password = 'password'

    def __init__(self):
        super(Iguana, self).__init__()

    def api(self, url, payload=None):
        if not url.startswith('http://'):
            url = self.url_base + url
        ret = requests.post(url, auth=(self.user, self.password), data=payload)
        return ret.text

    def version(self):
        ver = json.loads(self.api('current_version'))
        v = Version(ver['Major'], ver['Minor'], ver['Build'], ver['BuildExt'])
        return v

    def monitor(self):
        m = self.api('monitor_query')
        return m

    def log_messages(self):
        return self.api('api_query')

    def server_config(self):
        config = self.api('get_server_config')
        return config

    def default_config(self, source, destination):
        default_config = self.api('get_default_config', {'source':source, 'destination': destination})
        return default_config

    def channel_create(self, channel):
        raise NotImplementedError

    def channel_update(self, channel):
        raise NotImplementedError

    def channel_remove(self, channel):
        raise NotImplementedError

    def status(self):
        stat = self.api('status')
        return stat

    def channel_start(self, channel):
        raise NotImplementedError

    def channel_stop(self, channel):
        raise NotImplementedError

    def channel_restart(self, channel):
        self.stop_channel(channel)
        self.start_channel(channel)

    def channel_stop_all(self):
        stat = self.api('status', {'action': 'stopall'})
        return stat

    def channel_start_all(self):
        stat = self.api('status', {'action': 'startall'})
        return stat

    def channel_restart_all(self):
        self.stop_all_channels()
        self.start_all_channels()
        return stat


if __name__ == '__main__':
    i = Iguana()
    print(i.version())
#    print(i.default_config('LLP Listener', 'To Database'))
#    print(i.status())
#    print(i.monitor())
    print(i.log_messages())
