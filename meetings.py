"""Meeting errbot plugin."""
import datetime
import pprint

import reunion
from errbot import BotPlugin, botcmd


class Meeting(BotPlugin):
    """Meeting plugin."""

    def __init__(self, *args, **kwargs):
        """Init."""
        super().__init__(*args, **kwargs)

    def _format_channel(self, name):
        name = str(name)
        chars = ["!", "@", "#", "$", "^", "*"]
        for char in chars:
            name = name.replace(char, "")
        return name

    def callback_message(self, msg):
        """Message callback."""
        message = msg.body
        username = msg.frm
        channel_raw = msg.frm.room if msg.is_group else msg.frm
        meeting_message = f"{username}: {message}"

        if not message:
            return

        channel = self._format_channel(channel_raw)

        if "#startmeeting" in message:
            if channel in self.get("active_meetings", ()):
                self.send(
                    username, f"A meeting is currently in progress for {channel}."
                )
            else:
                self.send(username, f"A meeting is starting in {channel}.")
                self._create_meeting(channel)

        if channel in self.get("active_meetings", ()):
            self._add_message_to_history(channel, meeting_message)

        if "#endmeeting" in message:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
            if channel not in self.get("archived_meetings", {}):
                archive_meetings = self.get("archived_meetings", {})
                archive_meetings.update({channel: {}})
                self["archived_meetings"] = archive_meetings

            if channel in self.get("active_meetings", ()):
                all_archived_meetings = self["archived_meetings"]
                all_archived_meetings[channel].update(
                    {timestamp: self["raw_meetings"][channel]}
                )
                self["archived_meetings"] = all_archived_meetings
                self.send(
                    username,
                    f"Meeting results are stored in {channel}_{timestamp}.",
                )
                self._destroy_active_meeting(channel)
            else:
                self.send(
                    username,
                    f"Sorry, no active meeting found for {channel}.",
                )

    def _create_meeting(self, channel):
        """Create meeting storage if necessary."""
        if "active_meetings" not in self:
            self["active_meetings"] = set()
        channel = self._format_channel(channel)

        actives = self["active_meetings"]
        actives.add(channel)
        self["active_meetings"] = actives
        self._create_raw_meeting(channel)

    def _create_raw_meeting(self, channel):
        if channel not in self.get("raw_meetings", []):
            raw_meetings = self.get("raw_meetings", {})
            raw_meetings.update({channel: []})
            self["raw_meetings"] = raw_meetings

    def _add_message_to_history(self, channel, msg):
        self._create_raw_meeting(channel)
        if msg:
            all_history = self["raw_meetings"]
            all_history[channel].append(msg)
            self["raw_meetings"] = all_history

    def _destroy_history_meeting(self, meeting):
        channel, _, date = meeting.partition("_")
        all_meetings = self["archived_meetings"][channel]
        all_meetings.pop(date)
        self["archived_meetings"][channel] = all_meetings

    def _destroy_active_meeting(self, channel):
        """Destroy meeting from active list."""
        actives = self["active_meetings"]
        actives.discard(channel)
        self["active_meetings"] = actives

        raw_meetings = self["raw_meetings"]
        raw_meetings.pop(channel)
        self["raw_meetings"] = raw_meetings

    @botcmd(template="results")
    def meeting_summary(self, msg, args):
        """Meeting summary."""
        if args.startswith("active"):
            return "Sorry, cannot summarize active meetings"

        channel, _, timestamp = args.partition("_")
        try:
            raw_meeting = self["archived_meetings"][channel][timestamp]
        except KeyError:
            return "Meeting not found."

        meeting = reunion.Meeting()
        for entry in raw_meeting:
            meeting.parse(entry)

        data = {
            "meeting": meeting.results,
        }
        return data

    @botcmd
    def meeting_history(self, msg, args):
        """List all meetings."""
        for channel in self.get("archived_meetings", []):
            for date in self["archived_meetings"][channel]:
                yield f"{channel}_{date}"

        if not self.get("archived_meetings", []):
            yield "No historical meetings available."

    @botcmd
    def meeting_active(self, msg, args):
        """List of active meetings."""
        actives = self.get("active_meetings", ())
        if actives:
            active_meetings = ", ".join(actives)
        else:
            active_meetings = "There are no active meetings."
        yield active_meetings

    @botcmd
    def meeting_delete(self, msg, args):
        """List of active meetings."""
        if args.startswith("active"):
            active, _, channel = args.partition("_")
            self._destroy_active_meeting(channel)
            return f"Deleted active meeting: {args}"

        self._destroy_history_meeting(args)
        return f"Deleted meeting: {args}"
