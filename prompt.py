import menu
import state

__author__ = 'co'


def start_accept_reject_prompt(state_stack, game_state, message):
    prompt = menu.AcceptRejectPrompt(state_stack, message)
    game_state.start_prompt(state.UIState(prompt))
    return prompt.result