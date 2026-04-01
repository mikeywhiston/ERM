import discord

class FakeMessage:
    # 📝 Mock Discord message for utility testing
    def __init__(self, content, author, channel, state):
        self.content = content
        self.author = author  
        self.channel = channel 
        self.guild = author.guild if hasattr(author, 'guild') else None
        self.created_at = discord.utils.utcnow()
        self._state = state
        self.attachments = []
        self.mentions = []
        self.mention_everyone = False
        self.role_mentions = []