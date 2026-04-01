# This is used solely for the setup command
# stores current view information for utilisation
# of a view state variable without unintended
# cross-server data manipulation and consequences


class ViewStateManager(dict):
    # 📦 Manager for setup view states
    def __getitem__(self, key): # 📥 Retrieve item from state
        return super().__getitem__(key) # 📤 Return stored value

    # 📥 Set a view state item
    def __setitem__(self, key, value) -> None: # 📝 Store item in state
        return super().__setitem__(key, value) # ✅ Complete storage
