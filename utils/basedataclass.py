class BaseDataClass:
    # 🏗️ Base data class for mapping kwargs to attributes
    def __init__(self, *args, **kwargs): # 🛠️ Initialize with dynamic arguments
        for key, value in kwargs.items(): # 🔁 Iterate through key-value pairs
            setattr(self, key, value) # 🏷️ Set attribute dynamically
