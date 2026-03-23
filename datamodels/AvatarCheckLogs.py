from utils.mongo import Document
from utils.basedataclass import BaseDataClass


class AvatarCheckLog(BaseDataClass):
    guild_id: int
    username: str
    user_id: int
    passed: bool
    reason: str
    action: str
    avatar_url: str
    timestamp: int


class AvatarCheckLogs(Document):
    pass
