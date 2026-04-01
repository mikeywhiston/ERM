from typing import Dict, Set # 📝 Type hinting


class UsernameChecker:
    # 🕵️ Utility to check for unrealistic or problematic usernames
    def __init__(self): # 🏗️ Initialize checker
        self.similar_chars: Dict[str, str] = { # 🖼️ Lookalike characters
            "l": "I1|",  # lowercase L, uppercase i, one, pipe
            "O": "0",  # uppercase O, zero
            "i": "l1|",  # lowercase i, lowercase L, one, pipe
            "I": "l1|",  # uppercase i, lowercase L, one, pipe
        }
        self.confused_chars: Set[str] = set("Il1|O0") # 🔠 Characters often confused

    # 🧐 Check if a username is likely problematic
    def is_unrealistic(self, username: str) -> bool: # 🕵️ Problem detection
        """
        Check if a username appears to be unrealistic/problematic.
        Returns True if the username is likely to be problematic.
        """
        if not username: # ❓ Empty check
            return False # ✅ All good

        # Convert username to a simplified pattern
        consecutive_similar = 0 # 🔢 Streak counter

        for char in username: # 🔁 Iterate characters
            is_similar = False # 🚩 Detection flag
            for group in self.similar_chars.values(): # 🔁 Iterate clusters
                if char in group: # 🔍 Match found
                    consecutive_similar += 1 # 📈 Increment streak
                    is_similar = True # ✅ Set flag
                    break # ⏹️ Exit inner loop

            if not is_similar: # ❓ Streak broken
                if (
                    consecutive_similar >= 3 # 🛑 threshold reached
                ):  # If we found 3 or more similar characters in a row
                    return True # 🚨 Unrealistic detected
                consecutive_similar = 0 # 🧹 Reset counter

        # Check final count of consecutive similar characters
        if consecutive_similar >= 3: # 🛑 End of string check
            return True # 🚨 Unrealistic detected

        # Check if more than 50% of the username consists of commonly confused characters
        confused_char_count = sum(1 for c in username if c in self.confused_chars) # 🧮 Tally confusion
        if len(username) > 4 and confused_char_count / len(username) > 0.5: # 📈 Ratio check
            return True # 🚨 Suspicious composition

        return False # ✅ Username seems valid
