from altscore import AltScoreAsync as AltScore
from decouple import config
import asyncio


async def test():
    altscore = AltScore(
        client_id=config("ALTSCORE_CLIENT_ID"),
        client_secret=config("ALTSCORE_CLIENT_SECRET"),
        environment=config("ALTSCORE_ENVIRONMENT")
    )
    usecases = await altscore.borrower_central.usecases.retrieve_all()
    print(usecases[0])


if __name__ == '__main__':
    asyncio.run(test())
