import unittest

from sunrise.core.linguistic_manipulation import (
    apply_inflection,
    gerundise_word,
    past_tense_word,
    pluralise_word,
    Inflection
)


class LinguisticManipulationTests(unittest.TestCase):
    def test_pluralise_word_standard_and_sibilants(self) -> None:
        """Tests standard -s and sibilant endings (-x, -s, -z, -ch, -sh) requiring -es."""
        self.assertEqual(pluralise_word("cat"), "cats")
        self.assertEqual(pluralise_word("box"), "boxes")
        self.assertEqual(pluralise_word("bus"), "buses")
        self.assertEqual(pluralise_word("quiz"), "quizzes")
        self.assertEqual(pluralise_word("church"), "churches")
        self.assertEqual(pluralise_word("wish"), "wishes")

    def test_pluralise_word_y_endings(self) -> None:
        """Tests consonant+y -> ies and vowel+y -> ys."""
        self.assertEqual(pluralise_word("city"), "cities")
        self.assertEqual(pluralise_word("puppy"), "puppies")
        self.assertEqual(pluralise_word("boy"), "boys")
        self.assertEqual(pluralise_word("day"), "days")

    def test_pluralise_word_f_and_fe_endings(self) -> None:
        """Tests -f/-fe -> -ves transitions, and exceptions."""
        self.assertEqual(pluralise_word("leaf"), "leaves")
        self.assertEqual(pluralise_word("knife"), "knives")
        self.assertEqual(pluralise_word("wolf"), "wolves")
        self.assertEqual(pluralise_word("chef"), "chefs")

    def test_pluralise_word_irregular_and_mutated(self) -> None:
        """Tests completely mutated plurals and unchanging words."""
        self.assertEqual(pluralise_word("child"), "children")
        self.assertEqual(pluralise_word("foot"), "feet")
        self.assertEqual(pluralise_word("man"), "men")
        self.assertEqual(pluralise_word("mouse"), "mice")
        self.assertEqual(pluralise_word("tooth"), "teeth")
        self.assertEqual(pluralise_word("sheep"), "sheep")
        self.assertEqual(pluralise_word("fish"), "fish")
        self.assertEqual(pluralise_word("deer"), "deer")

    def test_pluralise_word_preserves_capitalisation(self) -> None:
        """Test that pluralisation preserves capitalisation as best as possible"""
        self.assertEqual(pluralise_word("Child"), "Children")
        self.assertEqual(pluralise_word("BOX"), "BOXES")
        self.assertEqual(pluralise_word("City"), "Cities")

    def test_gerundise_word_consonant_doubling_cvc(self) -> None:
        """Tests short Consonant-Vowel-Consonant words that MUST double the end letter."""
        self.assertEqual(gerundise_word("run"), "running")
        self.assertEqual(gerundise_word("pop"), "popping")
        self.assertEqual(gerundise_word("sit"), "sitting")
        self.assertEqual(gerundise_word("swim"), "swimming")
        self.assertEqual(gerundise_word("hop"), "hopping")

    def test_gerundise_word_cvc_exceptions(self) -> None:
        """Tests words which are CVC but don't double."""
        self.assertEqual(gerundise_word("row"), "rowing")
        self.assertEqual(gerundise_word("fix"), "fixing")
        self.assertEqual(gerundise_word("play"), "playing")

    def test_gerundise_word_silent_e(self) -> None:
        """Tests dropping the silent -e before adding -ing."""
        self.assertEqual(gerundise_word("make"), "making")
        self.assertEqual(gerundise_word("move"), "moving")
        self.assertEqual(gerundise_word("shave"), "shaving")
        self.assertEqual(gerundise_word("see"), "seeing")

    def test_gerundise_word_ie_endings(self) -> None:
        """Tests the -ie -> -ying rule."""
        self.assertEqual(gerundise_word("lie"), "lying")
        self.assertEqual(gerundise_word("die"), "dying")
        self.assertEqual(gerundise_word("tie"), "tying")
        self.assertEqual(gerundise_word("untie"), "untying")

    def test_irregular_gerunds(self) -> None:
        """Test irregular gerunds."""
        self.assertEqual(gerundise_word("larp"), "larping")
        self.assertEqual(gerundise_word("mine"), "mining")

    def test_past_tense_regular_and_e_drop(self) -> None:
        """Tests basic -ed additions and single -e mergers."""
        self.assertEqual(past_tense_word("jump"), "jumped")
        self.assertEqual(past_tense_word("play"), "played")
        self.assertEqual(past_tense_word("move"), "moved")
        self.assertEqual(past_tense_word("shave"), "shaved")
        self.assertEqual(past_tense_word("die"), "died")

    def test_past_tense_y_endings(self) -> None:
        """Tests consonant+y -> ied vs vowel+y -> yed."""
        self.assertEqual(past_tense_word("carry"), "carried")
        self.assertEqual(past_tense_word("cry"), "cried")
        self.assertEqual(past_tense_word("stay"), "stayed")

    def test_past_tense_consonant_doubling(self) -> None:
        """Tests past tense CVC doubling rules."""
        self.assertEqual(past_tense_word("pop"), "popped")
        self.assertEqual(past_tense_word("hop"), "hopped")
        self.assertEqual(past_tense_word("hug"), "hugged")

    def test_past_tense_irregular_mutations(self) -> None:
        """Stress tests common irregular English verbs."""
        self.assertEqual(past_tense_word("write"), "wrote")
        self.assertEqual(past_tense_word("speak"), "spoke")
        self.assertEqual(past_tense_word("eat"), "ate")
        self.assertEqual(past_tense_word("sleep"), "slept")
        self.assertEqual(past_tense_word("swim"), "swam")
        self.assertEqual(past_tense_word("go"), "went")
        self.assertEqual(past_tense_word("run"), "ran")
        self.assertEqual(past_tense_word("hit"), "hit")

    def test_apply_inflection_supports_multiple_forms(self) -> None:
        self.assertEqual(apply_inflection("feel", form=Inflection.GERUND), "feeling")
        self.assertEqual(apply_inflection("feeling", form=Inflection.PLURAL), "feelings")
        self.assertEqual(apply_inflection("shave", form=Inflection.GERUND), "shaving")
        self.assertEqual(apply_inflection("shaving", form=Inflection.PLURAL), "shavings")


if __name__ == "__main__":
    unittest.main()