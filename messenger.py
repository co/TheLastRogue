class Messenger(object):
    def __init__(self):
        self._messages = []
        self.new_message = False

    def message(self, new_message):
        new_message = Message(new_message)
        old_message = next((message for message in self._messages
                           if message.message == new_message.message and
                              message.ttl == new_message.ttl), None)
        if old_message is None:
            self._messages.append(new_message)
        else:
            old_message.increase()
        self.new_message = True

    def tail(self, length):
        self.new_message = False
        self._messages = [message for message in self._messages if message.ttl > 0]
        map(lambda m: m.tick(), self._messages)
        return self._messages[-length:]


class Message(object):
    def __init__(self, message, turn_created=None):
        self.message = message
        self.count = 1
        self.ttl = 5

    def increase(self):
        self.count += 1

    def tick(self):
        self.ttl -= 1

    def __str__(self):
        if self.count > 1:
            return str(self.message) + " x" + str(self.count)
        return str(self.message)


messenger = Messenger()
