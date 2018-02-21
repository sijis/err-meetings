"""Meeting errbot plugin."""
import pprint

import reunion
from errbot import BotPlugin, botcmd


class Meeting(BotPlugin):
    """Meeting plugin."""

    def __init__(self, *args, **kwargs):
        """Init."""
        self.meeting = reunion.Meeting()
        super().__init__(*args, **kwargs)

    def callback_message(self, msg):
        """Message callback."""
        message = msg.body
        username = msg.frm
        channel = msg.frm.room if msg.is_group else msg.frm
        meeting_message = '{username}: {message}'.format(username=username, message=message)

        self.meeting.parse(meeting_message)

        if '#startmeeting' in message and self.meeting._started:
            self.send(username, 'A meeting is starting in {}.'.format(channel))

        if not message:
            return

    @botcmd
    def meeting_results(self, msg, args):
        """Meeting results."""
        return pprint.pformat(self.meeting.results)
