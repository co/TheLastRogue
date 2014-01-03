from unittest import TestCase
import compositereader

__author__ = 'co'


class TestCompositeReader(TestCase):

    def test_get_first_word_if_any_handles_empty_string(self):
        self.assertIsNone(compositereader.get_first_word_if_any(""))

    def test_get_first_word_if_any_handles_single_word(self):
        self.assertEqual(compositereader.get_first_word_if_any("Word"), "Word")

    def test_get_first_word_if_any_handles_multiple_word(self):
        self.assertEqual(compositereader.get_first_word_if_any("CO Word"), "CO")

    def test_get_first_word_if_any_handles_white_space(self):
        self.assertEqual(compositereader.get_first_word_if_any("    \t \t \r \n CO \r \nWord"), "CO")

    def test_line_is_comment_if_line_starts_with_hash(self):
        self.assertTrue(compositereader.line_is_comment("# A comment."))

    def test_line_is_not_comment_if_doesnt_line_starts_with_hash(self):
        self.assertFalse(compositereader.line_is_comment("Not a comment."))

    def test_line_is_comment_handle_white_space(self):
        self.assertTrue(compositereader.line_is_comment("    \t \t \r \n # A comment."))

    def test_line_is_composite_definition(self):
        self.assertTrue(compositereader.line_is_composite_definition("Health"))

    def test_line_is_not_composite_definition(self):
        self.assertFalse(compositereader.line_is_composite_definition(" Health"))

    def test_lines_to_library_should_return_empty_dictionary_if_no_lines(self):
        self.assertEqual(compositereader.lines_to_library([]), {})

    def test_lines_to_library_should_get_composite_definition(self):
        lines = [
            "",
            "#",
            "Health"
        ]
        self.assertTrue("Health" in compositereader.lines_to_library(lines))

    def test_lines_to_library_should_get_composite_definition_and_components(self):
        lines = [
            "",
            "#",
            "Monster",
            "    hp 10-15",
            "    what 1 2 3 4 5",
            "    who",
            "    name CO"
        ]
        #Use assert Equals
        self.assertTrue("Monster" in compositereader.lines_to_library(lines))
        self.assertTrue(["10-15"] == compositereader.lines_to_library(lines)["Monster"]["hp"])
        self.assertTrue(["1", "2", "3", "4", "5"] == compositereader.lines_to_library(lines)["Monster"]["what"])
        self.assertTrue([] == compositereader.lines_to_library(lines)["Monster"]["who"])
        self.assertTrue(["CO"] == compositereader.lines_to_library(lines)["Monster"]["name"])

    def test_lines_to_library_should_get_multiple_composite_definitions_and_components(self):
        lines = [
            "",
            "#",
            "Monster",
            "    hp 10-15",
            "    what 1 2 3 4 5",
            "    who",
            "    name CO",
            "Frog",
            "    hp 40-45",
            "    walker 123",
            '    name "The Frog King"'
        ]
        #Use assert Equals
        self.assertTrue("Monster" in compositereader.lines_to_library(lines))
        self.assertTrue(["10-15"] == compositereader.lines_to_library(lines)["Monster"]["hp"])
        self.assertTrue(["1", "2", "3", "4", "5"] == compositereader.lines_to_library(lines)["Monster"]["what"])
        self.assertTrue([] == compositereader.lines_to_library(lines)["Monster"]["who"])
        self.assertTrue(["CO"] == compositereader.lines_to_library(lines)["Monster"]["name"])

        self.assertTrue("Frog" in compositereader.lines_to_library(lines))
        self.assertTrue(["40-45"] == compositereader.lines_to_library(lines)["Frog"]["hp"])
        self.assertTrue(["123"] == compositereader.lines_to_library(lines)["Frog"]["walker"])
        self.assertTrue(['The Frog King'] == compositereader.lines_to_library(lines)["Frog"]["name"])
