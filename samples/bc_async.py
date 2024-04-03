from altscore import AltScoreAsync as AltScore
from decouple import config
import asyncio


async def test():
    altscore = AltScore(
        client_id=config("ALTSCORE_CLIENT_ID"),
        client_secret=config("ALTSCORE_CLIENT_SECRET"),
        environment=config("ALTSCORE_ENVIRONMENT")
    )
    data_models = await altscore.borrower_central.data_models.retrieve_all()
    print(data_models)


if __name__ == '__main__':
    asyncio.run(test())
