import typing # 📝 Import typing for type hinting
from decouple import config # ⚙️ Load environment variables
import aiohttp # 🌐 Asynchronous HTTP requests


class Punishment:
    # 📦 Punishment data model
    def __init__(self, text, prediction, confidence, *args, **kwargs): # 🏗️ Initialize punishment
        self.text = text # 📄 Punishment text
        self.prediction = prediction # 🔮 AI prediction
        self.confidence = confidence # 📊 Prediction confidence
        self.modified = kwargs.get("modified", False) # 🛠️ If prediction was manual


class AI:
    # 🤖 AI interaction handler
    def __init__(self, api_url, api_auth): # 🏗️ Initialize AI handler
        self.api_url = api_url # 🔗 API base URL
        self.api_auth = api_auth # 🔑 API authentication key

    # 🎯 Get recommended punishment from AI
    async def recommended_punishment(
        self, reason: str, past: typing.Union[list[str], None] # 📥 Input reason and history
    ) -> Punishment:
        if past is None: # ❓ Check if history is missing
            past = [] # 📁 Default to empty list
        async with aiohttp.ClientSession() as session: # 🚪 Open HTTP session
            async with session.post(
                f"{self.api_url}?auth={self.api_auth}&version=1", # 📡 API endpoint
                json=[reason], # 📤 Send reason data
            ) as resp:
                result = await resp.json() # 📥 Parse JSON response
                # # # print(result)
                if not past: # ❓ If no history exists
                    res = result[-1] # 🔝 Take latest result
                    return Punishment(
                        text=res["text"], # 📄 Set text
                        prediction=res["prediction"], # 🔮 Set prediction
                        confidence=res["confidence"], # 📊 Set confidence
                    )

            weights = {"Warning": 1, "Kick": 3, "Ban": 4, "BOLO": 4} # ⚖️ Scoring weights
            score = weights.get(result[0]["prediction"], 0) + sum( # 🧮 Calculate total score
                [weights.get(x, 0) for x in past] # 📈 Sum historical weights
            )
            # # # print(score)
            if result[-1]["prediction"] == "BOLO": # 🚓 Check if BOLO
                # return "BOLO"
                return Punishment(
                    text=result[-1]["text"], # 📄 Set text
                    prediction="BOLO", # 🚨 Set BOLO prediction
                    confidence=result[-1]["confidence"], # 📊 Set confidence
                    modified=True, # 🛠️ Mark as modified
                )
            if score < 3: # 📉 Low severity check
                # return "Warning"
                return Punishment(
                    text=result[-1]["text"], # 📄 Set text
                    prediction="Warning", # ⚠️ Set Warning prediction
                    confidence=result[-1]["confidence"], # 📊 Set confidence
                    modified=True, # 🛠️ Mark as modified
                )
            elif (score < 4) or score <= 5 and result[-1]["prediction"] == "Kick": # 👢 Mid severity
                return Punishment(
                    text=result[-1]["text"], # 📄 Set text
                    prediction="Kick", # 🦵 Set Kick prediction
                    confidence=result[-1]["confidence"], # 📊 Set confidence
                    modified=True, # 🛠️ Mark as modified
                )
            else: # 🚫 High severity else
                return Punishment(
                    text=result[-1]["text"], # 📄 Set text
                    prediction="Ban", # 🔨 Set Ban prediction
                    confidence=result[-1]["confidence"], # 📊 Set confidence
                    modified=True, # 🛠️ Mark as modified
                )
