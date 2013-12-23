EQUIP_MESSAGE = "%(source_entity)s equips %(item)s."
UNEQUIP_MESSAGE = "%(source_entity)s puts away %(item)s."
HEALTH_MESSAGE = "%(source_entity)s heals %(target_entity)s for %(health)s health."
DISSOLVE_MESSAGE = "%(source_entity)s dissolves %(target_entity)s for %(damage)s damage."
HIT_MESSAGE = "%(source_entity)s hits %(target_entity)s for %(damage)s damage."
MISS_MESSAGE = "%(source_entity)s misses %(target_entity)s."


class Messenger(object):
    def __init__(self):
        self._messages = []
        self.has_new_message = False
        self.new_message = None

    def message(self, new_message):
        print new_message, new_message.__class__
        new_message = Message(new_message)
        old_message = next((message for message in self._messages
                           if message.message == new_message.message and
                              message.ttl == new_message.ttl), None)
        if old_message:
            old_message.increase()
        else:
            print "YESS: ", new_message
            self._messages.append(new_message)
            print "LETS SEE:", [(message.message, message.ttl) for message in self._messages]
        self.has_new_message = True
        if self.new_message:
            print "WHATWHAT", self.new_message
        print "Yo!", self.has_new_message

    def tail(self, length):
        print "THIS:", [message.message for message in self._messages[-length:]]
        raise
        self.has_new_message = False
        print "YoYo!", self.has_new_message
        self._messages = [message for message in self._messages if message.ttl > 0]
        print "this:", [message.message for message in self._messages]
        map(lambda m: m.tick(), self._messages)
        print "THIS:", [message.message for message in self._messages[-length:]]
        return self._messages[-length:]


class Message(object):
    def __init__(self, message):
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


msg = Messenger()
