import turn


class Messenger(object):

    def __init__(self):
        self.__messages = []

    def message(self, new_message):
        print "got message: ", new_message
        new_message = Message(new_message)
        current_turn = turn.current_turn
        old_message = next((message for message in self.__messages
                           if message.message == new_message.message
                           and message.turn_created == current_turn), None)
        if(old_message is None):
            self.__messages.append(new_message)
        else:
            old_message.increase()

    def tail(self, length):
        return self.__messages[-length:]


class Message(object):
    def __init__(self, message, turn_created=None):
        self.message = message
        self.count = 1
        if(turn_created is None):
            self.turn_created = turn.current_turn

    def increase(self):
        self.count += 1

    def __str__(self):
        if self.count > 1:
            return str(self.message) + " x" + str(self.count)
        return str(self.message)

messenger = Messenger()
