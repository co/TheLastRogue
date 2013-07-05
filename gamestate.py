import inputhandler
import colors
import gui
import libtcodpy as libtcod
import vector2d


def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)


class GameStateStack(object):
    def __init__(self):
        self._stack = []

    def main_loop(self):
        while len(self._stack) > 0:
            state = self.peek()
            state.update()
            state.draw()
            libtcod.console_flush()

    def push(self, game_state):
        self._stack.append(game_state)

    def peek(self):
        return self._stack[-1]

    def pop(self):
        return self._stack.pop()


class GameState(object):
    def __init__(self):
        pass

    def update(self):
        pass

    def draw(self):
        pass


class Menu(GameState):
    def __init__(self, position, width, height):
        super(Menu, self).__init__()
        self._menu_items = ["XX_Menu_Item_XX"]
        self._selected_index = 0
        self._wrap = True
        self.position = position
        self.width = width
        self.height = height
        self._item_stack_panel = gui.StackPanel(vector2d.ZERO, self.width,
                                                self.height, colors.DB_BLACK)

    def update(self):
        key = inputhandler.get_keypress()
        if key == inputhandler.UP:
            self.index_decrease()
        if key == inputhandler.DOWN:
            self.index_increase()
        if key == inputhandler.ENTER:
            self.activate(self._selected_index)

        self._recreate_option_list()

    def _recreate_option_list(self):
        self._item_stack_panel.elements = []
        for index, item in enumerate(self._menu_items):
            if(index == self._selected_index):
                color = colors.TEXT_ACTIVE
            else:
                color = colors.TEXT_INACTIVE
            menu_item = gui.TextBox(item, vector2d.ZERO, self.width, 1, color)
            self._item_stack_panel.elements.append(menu_item)

    def activate(self, index):
        pass

    def index_increase(self):
        self._offset_index(1)

    def index_decrease(self):
        self._offset_index(-1)

    def _offset_index(self, offset):
        if(self._wrap):
    # Will behave strangely for when offset is less than -menu_size
            self._selected_index =\
                (offset + self._selected_index + len(self._menu_items))\
                % len(self._menu_items)
        else:
            self._selected_index = clamp(offset + self._selected_index, 0,
                                         len(self._menu_items) - 1)

    def draw(self):
        self._item_stack_panel.draw(self.position)


class MainMenu(Menu):
    def __init__(self, position, width, height):
        super(MainMenu, self).__init__(position, width, height)
        self.start_game_option = "Start Game"
        self.quit_option = "Quit"
        self._menu_items = [self.start_game_option, self.quit_option]

    def activate(self, index):
        selected_option = self._menu_items[self._selected_index]
        if(selected_option == self.start_game_option):
            pass
        elif(selected_option == self.quit_option):
            game_state_stack.pop()


game_state_stack = GameStateStack()
