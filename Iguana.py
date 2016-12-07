"""Access to the Iguana API."""
import requests
import json
from bs4 import BeautifulSoup


class Channel(object):
    """A Channel object to wrap aspects of a channel."""

    def __init__(self, config):
        """Build the Channel object."""
        super(Channel, self).__init__()
        self._soup = BeautifulSoup(config, 'html.parser')

    @property
    def name(self):
        """The name of the channel."""
        return self._soup.channel['name']

    @name.setter
    def name(self, new_name):
        """Change the name of the property."""
        self._soup.channel['name'] = new_name

    @property
    def start_automatically(self):
        return self._soup.channel['start_automatically']

    @start_automatically.setter
    def start_automatically(self, start):
        self._soup.channel['start_automatically'] = str(bool(start))

    @property
    def port(self):
        return self._soup.channel.from_llp_listener['port']

    @port.setter
    def port(self, new_port):
        self._soup.channel.from_llp_listener['port'] = str(new_port)

    @property
    def database_reconnection_interval(self):
        return self._soup.channel['database_reconnection_interval']

    @database_reconnection_interval.setter
    def database_reconnection_interval(self, interval):
        self._soup.channel['database_reconnection_interval'] = str(interval)

    @property
    def maximum_database_reconnections(self):
        return self._soup.channel['maximum_database_reconnections']

    @maximum_database_reconnections.setter
    def maximum_database_reconnections(self, connections):
        self._soup.channel['maximum_database_reconnections'] = str(connections)

    @property
    def database_timeout_seconds(self):
        return self._soup.channel['database_timeout_seconds']

    @database_timeout_seconds.setter
    def database_timeout_seconds(self, seconds):
        self._soup.channel['database_timeout_seconds'] = str(seconds)

    @property
    def action_on_parse_error(self):
        return self._soup.channel['action_on_parse_error']

    @action_on_parse_error.setter
    def action_on_parse_error(self, action):
        self._soup.channel['action_on_parse_error'] = str(action)

    @property
    def action_on_db_error(self):
        return self._soup.channel['action_on_db_error']

    @action_on_db_error.setter
    def action_on_db_error(self, action):
        self._soup.channel['action_on_db_error'] = str(action)

    def __str__(self):
        """Return a string of the config.

        This just puts the soup back into a string. It's what should be used
        for sending to the API. Create the config from defaults, make changes,
        then use this to build the XML for the APi call.
        """
        return str(self._soup)


class Version(object):
    """Simple version object to access system versions."""

    def __init__(self, major, minor, build, ext=0):
        """Create version object."""
        super(Version, self).__init__()
        self.major = major
        self.minor = minor
        self.build = build
        if len(ext) == 0:
            ext = 0
        self.ext = ext

    def __str__(self):
        """Convert version to a string."""
        ver = str(self.major) + '.' + str(self.minor) + '.' + str(self.build)
        if self.ext > 0:
            ver += '.' + str(self.ext)
        return ver


class Iguana(object):
    """Main wrapper used to access Iguana's API."""

    def __init__(self):
        """Build the Iguana object."""
        super(Iguana, self).__init__()
        # The default values here conform to the default/trial values.
        # These are probably usually wrong except in simple testing.
        self.url_base = 'http://localhost:6543/'
        self.user = 'admin'
        self.password = 'password'

    def api(self, url, payload=None):
        """Call the actual API."""
        if not url.startswith('http://'):
            url = self.url_base + url
        ret = requests.post(url, auth=(self.user, self.password), data=payload)
        return ret.text

    def version(self):
        """Get the version running on the server."""
        ver = json.loads(self.api('current_version'))
        v = Version(ver['Major'], ver['Minor'], ver['Build'], ver['BuildExt'])
        return v

    def monitor(self):
        """Some system monitoring values."""
        m = self.api('monitor_query')
        return m

    def log_messages(self):
        """Return various log messages."""
        return self.api('api_query')

    def server_config(self):
        """The overall system config."""
        config = self.api('get_server_config')
        return config

    def default_config(self, source, destination):
        """A default config for a new channel."""
        default_config = self.api('get_default_config',
                                  {'source': source,
                                   'destination': destination})
        return default_config

    def channel_create(self, channel):
        raise NotImplementedError

    def channel_update(self, channel):
        raise NotImplementedError

    def channel_remove(self, channel):
        raise NotImplementedError

    def status(self):
        """Return system status."""
        stat = self.api('status')
        return stat

    def channel_start(self, channel):
        raise NotImplementedError

    def channel_stop(self, channel):
        raise NotImplementedError

    def channel_restart(self, channel):
        """Restart a channel."""
        self.stop_channel(channel)
        self.start_channel(channel)

    def channel_stop_all(self):
        """Stop all channels."""
        stat = self.api('status', {'action': 'stopall'})
        return stat

    def channel_start_all(self):
        """Start all channels."""
        stat = self.api('status', {'action': 'startall'})
        return stat

    def channel_restart_all(self):
        """Retart all channels."""
        self.stop_all_channels()
        self.start_all_channels()
        return stat


if __name__ == '__main__':
    i = Iguana()
    print(i.version())
    config = i.default_config('LLP Listener', 'To Database')
    c = Channel(config)
    print(c.name)
    print(str(c))
    print('#######')
    c.name = 'Biff'
    print(str(c))
    print('#######')
    print(c.port)
    c.port = 12345
    print(str(c))

#    print(i.status())
#    print(i.monitor())
#    print(i.log_messages())
