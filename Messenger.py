import collections
import turn


class Messenger(object):

    def __init__(self):
        self.__messages = []
        self.__new_messages_counter = collections.OrderedDict()

    def message(self, message):
        if(self.__new_messages_counter.get(message, None) is None):
            self.__new_messages_counter[message] = 1
        else:
            self.__new_messages_counter[message] =\
                self.__new_messages_counter[message] + 1

    def tail(self, length):
        return self.__messages[-length:]

    def push_new_messages(self):
        for message, count in self.__new_messages_counter.items():
            self.__messages.append(self.__get_line_with_repeat_count(message,
                                                                     count))
        self.__new_messages_counter = collections.OrderedDict()

    @staticmethod
    def __get_line_with_repeat_count(message, repeat_count):
        if(repeat_count <= 1):
            return message
        else:
            return message + " x" + str(repeat_count)

messenger = Messenger()


class Message(object):
    def __init__(self, message, turn_created=None):
        self.message = message
        if(turn_created is None):
            self.turn_created = turn.current_turn

    def __str__(self):
        return self.message
