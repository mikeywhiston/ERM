class BaseDataClass:
    # 🏗️ Base data class for mapping kwargs to attributes
    def __init__(self, *args, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
