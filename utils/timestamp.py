# 🕒 Format a timedelta object into a human-readable string
def td_format(td_object): # ⏲️ Time formatter
    seconds = int(td_object.total_seconds()) # 🔢 Get total seconds

    if seconds == 0: # ❓ Exactly zero
        return "0 seconds" # 📤 Return zero string

    if seconds < 0: # ⏪ Negative duration
        new_seconds = abs(seconds) # ➕ Convert to positive
        periods = [ # 🗓️ Time units
            ("year", 60 * 60 * 24 * 365),
            ("month", 60 * 60 * 24 * 30),
            ("day", 60 * 60 * 24),
            ("hour", 60 * 60),
            ("minute", 60),
            ("second", 1),
        ]

        strings = [] # 📁 String storage
        for period_name, period_seconds in periods: # 🔁 Iterate units
            if new_seconds >= period_seconds: # ❓ Fits in unit
                period_value, new_seconds = divmod(new_seconds, period_seconds) # 🧮 Calculate count
                has_s = "s" if period_value > 1 else "" # 🔠 Pluralization
                strings.append("%s %s%s" % (period_value, period_name, has_s)) # 📝 Add to list
        if strings is not []: # ✅ Found components
            stri = ", ".join(strings) # 🔗 Join with commas
            stri = "-" + stri # ➖ Add negative sign
            return stri # 📤 Return formatted string
        else:
            raise ValueError("Time delta is too small") # 💥 Error if empty

    periods = [ # 🗓️ Time units (positive)
        ("year", 60 * 60 * 24 * 365),
        ("month", 60 * 60 * 24 * 30),
        ("day", 60 * 60 * 24),
        ("hour", 60 * 60),
        ("minute", 60),
        ("second", 1),
    ]

    strings = [] # 📁 String storage
    for period_name, period_seconds in periods: # 🔁 Iterate units
        if seconds >= period_seconds: # ❓ Fits in unit
            period_value, seconds = divmod(seconds, period_seconds) # 🧮 Calculate count
            has_s = "s" if period_value > 1 else "" # 🔠 Pluralization
            strings.append("%s %s%s" % (period_value, period_name, has_s)) # 📝 Add to list
    if strings is not []: # ✅ Found components
        return ", ".join(strings) # 📤 Return formatted string
    else:
        raise ValueError("Time delta is too small") # 💥 Error if empty
