"""Meeting errbot plugin."""
import datetime
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

        if not message:
            return

        self.meeting.parse(meeting_message)

        if '#startmeeting' in message and self.meeting._started:
            self.send(username, 'A meeting is starting in {}.'.format(channel))

        if '#endmeeting' in message and not self.meeting._started:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M')
            channel = '{}'.format(channel)
            self[channel] = {timestamp: self.meeting.results['discussion']}
            self.send(username, 'Meeting results are stored in {}_{}.'.format(channel, timestamp))


    @botcmd(template='results')
    def meeting_results(self, msg, args):
        """Meeting results."""
        channel, date, hour = args.split('_')
        timestamp = '{}_{}'.format(date, hour)
        raw_meeting = self[channel][timestamp]

        meeting = reunion.Meeting()
        for entry in raw_meeting:
            meeting.parse(entry)

        data = {
            'meeting': meeting.results,
        }
        return data

    @botcmd
    def meeting_list(self, msg, args):
        """List all meetings."""
        for channel in self:
            for date in self[channel]:
                yield '{channel}_{date}'.format(channel=channel, date=date)
