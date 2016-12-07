"""Access to the Iguana API."""
from bs4 import BeautifulSoup
from distutils.version import LooseVersion
import json
import requests


class Channel(object):
    """A Channel object to wrap aspects of a channel.

    This should be used by sending a default config on object creation
    (see Iguana.default_config()). Once created, you can edit the config
    with the various properties of this object. Return the resulting
    XML by just getting the string version of this, and then pass that
    back to the Iguana object to do what you want with it - add/edit/delete
    the channel.

    >>> i = Iguana()
    >>> c = Channel(i.default_config('LLP Listener', 'To Database'))
    >>> c.name = 'channeltest'
    >>> c.port = 12345
    >>> i.channel_create(c)
    """

    def __init__(self, config):
        """Build the Channel object."""
        super(Channel, self).__init__()
        self._soup = BeautifulSoup(str(config), 'html.parser')

    @property
    def name(self):
        """The name of the channel."""
        return self._soup.channel['name']

    @name.setter
    def name(self, new_name):
        self._soup.channel['name'] = new_name

    @property
    def start_automatically(self):
        """True if the channel is set to start automatically."""
        return self._soup.channel['start_automatically']

    @start_automatically.setter
    def start_automatically(self, start):
        self._soup.channel['start_automatically'] = str(bool(start))

    @property
    def port(self):
        """Return the port this channel listens to."""
        return self._soup.channel.from_llp_listener['port']

    @port.setter
    def port(self, new_port):
        self._soup.channel.from_llp_listener['port'] = str(new_port)

    @property
    def database_reconnection_interval(self):
        """The time between reconnection attempts."""
        return self._soup.channel['database_reconnection_interval']

    @database_reconnection_interval.setter
    def database_reconnection_interval(self, interval):
        self._soup.channel['database_reconnection_interval'] = str(interval)

    @property
    def maximum_database_reconnections(self):
        """The number of reconnection attempts."""
        return self._soup.channel['maximum_database_reconnections']

    @maximum_database_reconnections.setter
    def maximum_database_reconnections(self, connections):
        self._soup.channel['maximum_database_reconnections'] = str(connections)

    @property
    def database_timeout_seconds(self):
        """Time before giving up on a database connection."""
        return self._soup.channel['database_timeout_seconds']

    @database_timeout_seconds.setter
    def database_timeout_seconds(self, seconds):
        self._soup.channel['database_timeout_seconds'] = str(seconds)

    @property
    def action_on_parse_error(self):
        """Action to be taken on a parse error.

        Choose 'skip' to ignore errors and continue parsing.
        """
        return self._soup.channel['action_on_parse_error']

    @action_on_parse_error.setter
    def action_on_parse_error(self, action):
        self._soup.channel['action_on_parse_error'] = str(action)

    @property
    def action_on_db_error(self):
        """Action to be taken on a database error.

        Choose 'skip' to ignore errors and continue sending remaining data.
        """
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


class IguanaApiRresult(object):
    """Used to hold the return values in an API return call from Iguana."""

    def __init__(self, message):
        """Build the IguanaApiRresult object."""
        super(IguanaApiRresult, self).__init__()
        self.status = 0
        self.text = ''
        self._parse_message(message)

    def _parse_message(self, msg):
        """Simple parsing to see if we have an error return from the API."""
        try:
            result = json.loads(msg)
            if 'error' in result:
                self.status = result['error']['return_code']
                self.text = result['error']['description']
                return
        except ValueError:
            # ValueError (translating to 'this message isn't JSON', in this
            # case) means we got something decent - errors from the API come
            # to us as JSON. If it isn't JSON, it's not an error (and most
            # likely XML). Pass the contents up.
            pass

        self.status = 0
        self.text = msg

    def __int__(self):
        """The error code, if we have one."""
        return self.status

    def __str__(self):
        """The body of the message itself."""
        return self.text

    def __bool__(self):
        """True if we don't have an error."""
        return self.status == 0

    def __len__(self):
        """Length of the message."""
        return len(self.text)


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
        return IguanaApiRresult(ret.text)

    def version(self):
        """Get the version running on the server.

        Using LooseVersion() in case BuildExt is used and it'd probably be
        good to support that version tag if/when used. Sad, since
        StrictVersion() > LooseVersion() in almost every other way.

        Still, this gives us handy version comparisons if we want it.
        """
        ver = json.loads(str(self.api('current_version')))
        v = (str(ver['Major']) + '.' +
             str(ver['Minor']) + '.' +
             str(ver['Build']))

        if (len(ver['BuildExt']) > 0):
            v += '.' + ver['BuildExt']

        return LooseVersion(v)

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
        """Given a Channel object, create a new channel."""
        raise NotImplementedError

    def channel_update(self, channel):
        """Update an existing channel with this Channel object."""
        raise NotImplementedError

    def channel_remove(self, channel):
        """Remove this channel."""
        raise NotImplementedError

    def status(self):
        """Return system status."""
        stat = self.api('status')
        return stat

    def channel_config(self, guid, is_name=False):
        """Load a channel config and return it as a Channel object.

        Searching by GUID is recommended by INTERFACEWARE, but this can
        search by name as well. Set the 'is_name' value to True when doing so.
        """
        var = 'guid'
        if is_name:
            var = 'name'
        result = self.api('get_channel_config', {var: guid})
        if not result:
            return None

        return Channel(str(result))

    def channel_update(self, channel):
        """Update a channel from a Channel object."""
        if type(channel) is not Channel:
            raise TypeError('channel_update() requires a Channel object.')

        self.api('update_channel', {'config': channel})

    def channel_start(self, channel):
        """Start a channel."""
        raise NotImplementedError

    def channel_stop(self, channel):
        """Stop a channel."""
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
    c = Channel(i.default_config('LLP Listener', 'To Database'))
    c.name = 'channeltest123'
    c.port = 123
    i.channel_create(c)

    print(c)

#    print(i.status())
#    print(i.monitor())
#    print(i.log_messages())
