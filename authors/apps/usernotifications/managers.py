"""
manager module for user notifications

"""
from datetime import datetime
from django.contrib.contenttypes.models import ContentType
from actstream.managers import ActionManager, stream

class MyActionManager(ActionManager):
    @stream
    def mystream(self, obj, verb='posted', time=None):
        if time is None:
            time = datetime.now()
        return obj.actor_actions.filter(verb = verb, created_at__lte = time)