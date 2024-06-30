import discord
import unittest
from bot.utils.converters import guild_ids_to_guilds, list_to_table, pascal_to_snake, pascal_to_space


class TestConverters(unittest.TestCase):
    def test_list_to_table(self):
        # Test case 1: Empty table
        table_list = []
        expected_output = ""
        self.assertEqual(list_to_table(table_list), expected_output)

        # Test case 2: Table with one row
        table_list = [["Name", "Age", "Gender"]]
        expected_output = "Name    Age    Gender"
        self.assertEqual(list_to_table(table_list), expected_output)

        # Test case 3: Table with multiple rows
        table_list = [
            ["John", "25", "Male"],
            ["Jane", "30", "Female"],
            ["Sam", "40", "Male"]
        ]
        expected_output = "John    25    Male\nJane    30    Female\nSam     40    Male"
        self.assertEqual(list_to_table(table_list), expected_output)

        # Test case 4: Table with uneven column lengths
        table_list = [
            ["Name", "Age", "Gender"],
            ["John", "25", "Male"],
            ["Jane", "30", "Female"],
            ["Sam", "40", "Male"]
        ]
        expected_output = "Name    Age    Gender\nJohn    25     Male\nJane    30     Female\nSam     40     Male"
        self.assertEqual(list_to_table(table_list), expected_output)

    def test_guild_ids_to_guilds(self):
        # Test case 1: Empty list
        self.assertEqual(guild_ids_to_guilds([]), [])

        # Test case 2: List with guild IDs
        guild_ids = [123, 456, 789]
        expected_result = [discord.Object(id=123), discord.Object(
            id=456), discord.Object(id=789)]
        self.assertEqual(guild_ids_to_guilds(guild_ids), expected_result)

        # Test case 3: List with duplicate guild IDs
        guild_ids = [123, 123, 456, 789, 789]
        expected_result = [discord.Object(id=123), discord.Object(
            id=123), discord.Object(id=456), discord.Object(id=789), discord.Object(id=789)]
        self.assertEqual(guild_ids_to_guilds(guild_ids), expected_result)

        # Test case 4: List with negative guild IDs
        guild_ids = [-123, -456, -789]
        expected_result = [discord.Object(
            id=-123), discord.Object(id=-456), discord.Object(id=-789)]
        self.assertEqual(guild_ids_to_guilds(guild_ids), expected_result)

    def test_pascal_to_snake(self):
        # Test case 1: Empty string
        self.assertEqual(pascal_to_snake(""), "")

        # Test case 2: String with one word
        self.assertEqual(pascal_to_snake("Hello"), "hello")

        # Test case 3: String with multiple words
        self.assertEqual(pascal_to_snake("HelloWorld"), "hello_world")

        # Test case 4: String with numbers
        self.assertEqual(pascal_to_snake("Hello123World"), "hello123_world")

        # Test case 5: String with special characters
        self.assertEqual(pascal_to_snake("Hello@World"), "hello@_world")

    def test_pascal_to_space(self):
        # Test case 1: Empty string
        self.assertEqual(pascal_to_space(""), "")

        # Test case 2: String with one word
        self.assertEqual(pascal_to_space("Hello"), "Hello")

        # Test case 3: String with multiple words
        self.assertEqual(pascal_to_space("HelloWorld"), "Hello World")

        # Test case 4: String with numbers
        self.assertEqual(pascal_to_space("Hello123World"), "Hello123 World")

        # Test case 5: String with special characters
        self.assertEqual(pascal_to_space("Hello@World"), "Hello@ World")
