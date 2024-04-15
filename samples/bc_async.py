from altscore import AltScoreAsync as AltScore
from decouple import config
import asyncio


altscore = AltScore(
    client_id=config("ALTSCORE_CLIENT_ID"),
    client_secret=config("ALTSCORE_CLIENT_SECRET"),
    environment=config("ALTSCORE_ENVIRONMENT")
)

borrowers = asyncio.run(altscore.borrower_central.borrowers.retrieve_all())
