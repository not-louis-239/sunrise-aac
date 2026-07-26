# engine.py - core AAC engine for behind-the-scenes, or should I say, behind-the-screens logic

# repo at: https://github.com/not-louis-239/sunrise-aac
# Copyright (C) 2026 Louis Masarei-Boulton <243234869+not-louis-239@users.noreply.github.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


from typing import Any, Callable

import sunrise.core.linguistic_manipulation as lm
from sunrise.core.speak import speak, stop_speaking as _stop_speaking
from sunrise.core.language_tree import Button, LanguageTree, load_language_tree


class Word:
    """A class representing a word as a component of the sentence bar."""
    def __init__(self, word: str) -> None:
        self.base_string = word
        self.current_string = word
        self.transformations: list[lm.Inflection] = []

    def __str__(self) -> str:
        return self.current_string

    def transform(self, inf: lm.Inflection) -> None:
        """Transforms the word's current string according to the given `inf` and updates `self`'s
        transformation history."""
        self.current_string = lm.apply_inflection(word=self.current_string, form=inf)
        self.transformations.append(inf)

    def inflection_is_valid(self, inf: lm.Inflection) -> bool:
        """Returns True if, given the `Word`'s state, the `inf` is a valid transformation for the word."""
        return inf in lm.get_allowed_transformations(past_transformations=self.transformations)


class AACEngine:
    """The engine class for the AAC talker (AAC = Augmentative and Alternative Communication)."""

    FUNC_REGISTRY: dict[str, Callable[[Any], None]] = {}
    INFLECTION_FUNCS: dict[str, lm.Inflection] = {}  # takes the function alias, points to the inflection enum entry

    @classmethod
    def register(cls, func_alias: str, *, inf: lm.Inflection | None = None) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            AACEngine.FUNC_REGISTRY[func_alias] = func
            if inf is not None:
                AACEngine.INFLECTION_FUNCS[func_alias] = inf
            return func
        return decorator

    def get_func_options(self) -> list[str]:
        return list(self.FUNC_REGISTRY.keys())

    def __init__(self):
        self.sentence_bar: list[Word] = []
        self.history: list[str] = []  # list of folder IDs that the AACEngine has been to
        self.current_node: str = "HOME"
        self.tree: LanguageTree = load_language_tree()

    def _reset_history(self) -> None:
        self.current_node = "HOME"
        self.history.clear()

    def current_buttons(self) -> list[Button]:
        """Get the current buttons for the engine's current node,
        accounting for the universal node.
        If a node cannot be found in the language tree, it skips attempting
        to find buttons for the current node."""

        universal_node = self.tree.get("UNIVERSAL")
        node = self.tree.get(self.current_node)

        buttons: list[Button] = []

        if universal_node is not None:
            buttons.extend(universal_node.buttons)
        if node is not None:
            buttons.extend(node.buttons)

        return buttons

    def get_node_for_button(self, button: Button) -> str | None:
        for node_name in ["UNIVERSAL", self.current_node]:
            node = self.tree.get(node_name)
            if node and button in node.buttons:
                return node_name
        return None

    def on_button_press(self, button: Button) -> None:
        # Update destination if the button has one
        if button.dest is not None:
            if isinstance(button.dest, int):
                # Relative offset - repeatedly set the current node to the last item in the history
                # until history is exhausted or the destination is reached
                to_remove = -button.dest
                for _ in range(to_remove):
                    if self.history:
                        self.current_node = self.history.pop()
            else:
                if button.dest != "HOME":
                    self.history.append(self.current_node)
                self.current_node = button.dest

        # Clear history if at HOME or history is exhausted
        if self.current_node == "HOME" or not self.history:
            self._reset_history()

        # If the button has a word, speak and append to the sentence bar
        if button.word is not None:
            speak(button.word.lower())  # normalise so the speaking engine doesn't say "capital I"
            self.sentence_bar.append(Word(word=button.word))

        # If no word or dest, the button must have a function call inside of it
        if button.func is not None and (func := AACEngine.FUNC_REGISTRY.get(button.func)) is not None:
            if (inf := self.INFLECTION_FUNCS.get(button.func)) is not None:
                if self.sentence_bar and self.sentence_bar[-1].inflection_is_valid(inf):
                    func(self)
            else:
                func(self)

    def type_keyboard_char(self, char: str) -> None:
        if not self.sentence_bar:
            self.sentence_bar.append(Word(char))
            return

        self.sentence_bar[-1].current_string += char
        self.sentence_bar[-1].transformations.clear()

    def backspace_keyboard(self) -> None:
        if not self.sentence_bar:
            return

        self.sentence_bar[-1].current_string = self.sentence_bar[-1].current_string[:-1]
        self.sentence_bar[-1].transformations.clear()

        if not self.sentence_bar[-1].current_string:
            del self.sentence_bar[-1]


# Now for registry functions
@AACEngine.register("clear_sentence_bar")
def clear_sentence_bar(self: AACEngine) -> None:
    """Clear the sentence bar."""
    self.sentence_bar.clear()

@AACEngine.register("backspace_sentence_bar")
def backspace_sentence_bar(self: AACEngine) -> None:
    """Remove the last word from the sentence bar."""
    if self.sentence_bar:
        self.sentence_bar.pop()

@AACEngine.register("speak_sentence_bar")
def speak_sentence_bar(self: AACEngine) -> None:
    """Speak the current sentence bar."""
    sentence = " ".join(str(w) for w in self.sentence_bar)
    speak(sentence)

@AACEngine.register("stop_speaking")
def stop_speaking(self: AACEngine) -> None:
    """Stop any currently playing speech immediately."""
    _stop_speaking()

@AACEngine.register("pluralise", inf=lm.Inflection.PLURAL)
def pluralise(self: AACEngine) -> None:
    """Add an 's' to the last word in the sentence bar"""
    if not self.sentence_bar:
        return
    self.sentence_bar[-1].transform(inf=lm.Inflection.PLURAL)

@AACEngine.register("gerundise", inf=lm.Inflection.GERUND)
def gerundise(self: AACEngine) -> None:
    """Convert the last word in the sentence bar to its gerund form."""
    if not self.sentence_bar:
        return
    self.sentence_bar[-1].transform(inf=lm.Inflection.GERUND)

@AACEngine.register("make_past_tense", inf=lm.Inflection.PAST)
def make_past_tense(self: AACEngine) -> None:
    """Convert the last word in the sentence bar to its past tense."""
    if not self.sentence_bar:
        return
    self.sentence_bar[-1].transform(inf=lm.Inflection.PAST)

@AACEngine.register("agenticise", inf=lm.Inflection.AGENTIC)
def agenticise(self: AACEngine) -> None:
    """Convert the last word in the sentence bar to its agentic form."""
    if not self.sentence_bar:
        return
    self.sentence_bar[-1].transform(inf=lm.Inflection.AGENTIC)
