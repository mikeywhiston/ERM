import discord # 🎮 Import discord library

class FakeMessage:
    # 📝 Mock Discord message for utility testing
    def __init__(self, content, author, channel, state): # 🏗️ Initialize mock message
        self.content = content # 💬 Message content
        self.author = author  # 👤 Message author
        self.channel = channel # 📺 Channel context
        self.guild = author.guild if hasattr(author, 'guild') else None # 🏰 Guild reference
        self.created_at = discord.utils.utcnow() # ⏰ Message timestamp
        self._state = state # ⚙️ Internal state
        self.attachments = [] # 📎 Empty attachments list
        self.mentions = [] # 🔔 No mentions
        self.mention_everyone = False # 📣 Mention everyone off
        self.role_mentions = [] # 🛡️ No role mentions
