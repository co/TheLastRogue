from compositecore import Leaf
import menu
import state

__author__ = 'co'


def start_accept_reject_prompt(state_stack, game_state, message):
    prompt = menu.AcceptRejectPrompt(state_stack, message)
    game_state.start_prompt(state.UIState(prompt))
    return prompt.result


class PromptPlayer(Leaf):
    def __init__(self, message):
        super(PromptPlayer, self).__init__()
        self.tags = ["prompt_player"]
        self.text = message

    def prompt_player(self, **kwargs):
        target_entity = kwargs["target_entity"]
        return start_accept_reject_prompt(target_entity.game_state.value.menu_prompt_stack,
                                          target_entity.game_state.value, self.text)