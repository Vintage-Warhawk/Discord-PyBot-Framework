"""
File: emoji_converter.py
Maintainer: Vntage Warhawk
Last Edit: 2025-12-01

Description:
Utility helpers to convert user-entered emoji text into usable forms for
Discord's reaction API. Supports Unicode, emoji aliases, regional indicators,
and server custom emojis.
"""

import re
import discord
import emoji as emoji_lib


REGIONAL_OFFSET = ord("🇦")  # U+1F1E6


class EmojiConverter:
	"""
	Converts string representations of emojis into objects usable by Discord.
	"""

	@staticmethod
	def convert_emoji(text: str, guild: discord.Guild):
		"""
		Convert a supplied emoji (🔥, :name:, :regional_indicator_x:, <:name:id>, <a:name:id>)
		into something suitable for add_reaction().

		Returns:
			- unicode emoji (str)
			- discord.Emoji
			- discord.PartialEmoji
			- None (if invalid)
		"""
		if not text:
			return None

		text = text.strip()

		# 1. Unicode emoji (🔥)
		if EmojiConverter._is_unicode(text):
			return text

		# 2. :alias: or :regional_indicator_x:
		alias_match = re.fullmatch(r":([A-Za-z0-9_]+):", text)
		if alias_match:
			alias = alias_match.group(1)

			# Try to convert alias to Unicode
			unicode_candidate = EmojiConverter._alias_to_unicode(alias)
			if unicode_candidate:
				return unicode_candidate

			# Try guild custom emoji by name
			custom = discord.utils.get(guild.emojis, name=alias)
			if custom:
				return custom

			return None

		# 3. Discord markup <:name:id> or <a:name:id>
		markup = re.fullmatch(r"<(a?):(\w+):(\d+)>", text)
		if markup:
			animated = markup.group(1) == "a"
			emoji_id = int(markup.group(3))

			# Try to get the cached emoji
			obj = guild.get_emoji(emoji_id)
			if obj:
				return obj

			# Not cached → fallback to PartialEmoji
			return discord.PartialEmoji(id=emoji_id, animated=animated)

		# Nothing matched
		return None

	@staticmethod
	def _is_unicode(text: str) -> bool:
		"""
		Detect unicode emoji, including multi-codepoint glyphs.
		"""
		return any(ord(c) > 0x1F000 for c in text)

	@staticmethod
	def _alias_to_unicode(alias: str) -> str | None:
		"""
		Convert a standard emoji alias or Discord regional indicator to Unicode.
		Returns None if not found.
		"""
		# 1. Standard emoji library alias
		candidate = emoji_lib.emojize(f":{alias}:", language="alias")
		if candidate != f":{alias}:":
			return candidate

		# 2. Discord-style regional indicator
		if alias.startswith("regional_indicator_") and len(alias) == 20:
			letter = alias[-1].lower()
			if "a" <= letter <= "z":
				return chr(REGIONAL_OFFSET + ord(letter) - ord("a"))

		return None
