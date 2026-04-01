import collections # 🗄️ Standard collections
import logging # 📝 Logging module

"""
A helper file for using mongo db
Class document aims to make using mongo calls easy, saves
needing to know the syntax for it. Just pass in the db instance
on init and the document to create an instance on and boom
"""


class Document:
    # 🗄️ Helper class for MongoDB document operations
    def __init__(self, connection, document_name): # 🏗️ Initialize document helper
        """
        Our init function, sets up the conenction to the specified document
        Params:
         - connection (Mongo Connection) : Our database connection
         - documentName (str) : The document this instance should be
        """
        self.db = connection[document_name] # 🔗 Set document handle
        self.logger = logging.getLogger(__name__) # 📝 Set logger

    # <-- Pointer Methods -->
    # ⬆️ Wrapper for update_by_id
    async def update(self, dict): # 🔄 Update pointer
        """
        For simpler calls, points to self.update_by_id
        """
        await self.update_by_id(dict) # 🚀 Call actual update

    # 🔍 Wrapper for find_by_id
    async def get_by_id(self, id): # 🔍 Get pointer
        """
        This is essentially find_by_id so point to that
        """
        return await self.find_by_id(id) # 📥 Return found data

    # 🔎 Wrapper for find_by_id
    async def find(self, id): # 🔎 Find pointer
        """
        For simpler calls, points to self.find_by_id
        """
        return await self.find_by_id(id) # 📥 Return found data

    # 🗑️ Wrapper for delete_by_id
    async def delete(self, id): # 🗑️ Delete pointer
        """
        For simpler calls, points to self.delete_by_id
        """
        await self.delete_by_id(id) # 💣 Execute deletion

    # <-- Actual Methods -->
    # 🆔 Find a document by its ID
    async def find_by_id(self, id): # 📍 Targeted search
        """
        Returns the data found under `id`
        Params:
         -  id () : The id to search for
        Returns:
         - None if nothing is found
         - If somethings found, return that
        """
        return await self.db.find_one({"_id": id}) # 📥 Return single document

    # ❌ Delete a document by its ID
    async def delete_by_id(self, id): # 📍 Targeted deletion
        """
        Deletes all items found with _id: `id`
        Params:
         -  id () : The id to search for and delete
        """
        if not await self.find_by_id(id): # ❓ Document exists
            return # 🚫 Skip if missing

        await self.db.delete_many({"_id": id}) # 💣 Remove document(s)

    # ➕ Insert a new document
    async def insert(self, dict): # 📥 Store new data
        """
        insert something into the db
        Params:
        - dict (Dictionary) : The Dictionary to insert
        """
        # Check if it's actually a Dictionary
        if not isinstance(dict, collections.abc.Mapping): # 🛡️ Validation
            raise TypeError("Expected Dictionary.") # 💥 Wrong type

        # Always use your own _id
        if "_id" not in dict: # 🛡️ Required field check
            raise KeyError("_id not found in supplied dict.") # 💥 ID missing

        await self.db.insert_one(dict) # 📥 Perform insertion

    # 🔄 Update or insert a document
    async def upsert(self, dict): # 🔄 Smart update
        """
        Makes a new item in the document, if it already exists
        it will update that item instead
        This function parses an input Dictionary to get
        the relevant information needed to insert.
        Supports inserting when the document already exists
        Params:
         - dict (Dictionary) : The dict to insert
        """
        if await self.__get_raw(dict["_id"]) is not None:
            await self.update_by_id(dict)
        else:
            await self.db.insert_one(dict)

    # 📝 Update an existing document by ID
    async def update_by_id(self, dict):
        """
        For when a document already exists in the data
        and you want to update something in it
        This function parses an input Dictionary to get
        the relevant information needed to update.
        Params:
         - dict (Dictionary) : The dict to insert
        """
        # Check if its actually a Dictionary
        if not isinstance(dict, collections.abc.Mapping):
            raise TypeError("Expected Dictionary.")

        # Always use your own _id
        if "_id" not in dict:
            raise KeyError("_id not found in supplied dict.")

        if not await self.find_by_id(dict["_id"]):
            return

        id = dict["_id"]
        dict.pop("_id")
        await self.db.update_one({"_id": id}, {"$set": dict})

    # 📭 Remove a field from a document
    async def unset(self, dict):
        """
        For when you want to remove a field from
        a pre-existing document in the collection
        This function parses an input Dictionary to get
        the relevant information needed to unset.
        Params:
         - dict (Dictionary) : Dictionary to parse for info
        """
        # Check if its actually a Dictionary
        if not isinstance(dict, collections.abc.Mapping):
            raise TypeError("Expected Dictionary.")

        # Always use your own _id
        if "_id" not in dict:
            raise KeyError("_id not found in supplied dict.")

        if not await self.find_by_id(dict["_id"]):
            return

        id = dict["_id"]
        dict.pop("_id")
        await self.db.update_one({"_id": id}, {"$unset": dict})

    # ➕ Increment a numeric field
    async def increment(self, id, amount, field):
        """
        Increment a given `field` by `amount`
        Params:
        - id () : The id to search for
        - amount (int) : Amount to increment by
        - field () : field to increment
        """
        if not await self.find_by_id(id):
            return

        await self.db.update_one({"_id": id}, {"$inc": {field: amount}})

    # 📚 Get all documents in the collection
    async def get_all(self):
        """
        Returns a list of all data in the document
        """
        data = []
        async for document in self.db.find({}):
            data.append(document)
        return data

    # <-- Private methods -->
    # 🕵️ Get raw data for a document
    async def __get_raw(self, id):
        """
        An internal private method used to eval certain checks
        within other methods which require the actual data
        """
        return await self.db.find_one({"_id": id})
