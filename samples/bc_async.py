from altscore import AltScoreAsync as AltScore
from decouple import config
import asyncio


async def get_borrower():
    altscore = AltScore(api_key=config("ALTSCORE_API_KEY"))
    borrower = await altscore.borrower_central.borrowers.retrieve("dfaab9fd-d4eb-4f53-9070-f2605c4cc9e2")
    authorizations = await borrower.get_authorizations(key="bureau_authorization")

    if len(authorizations) > 0:
        last_auth = authorizations[0]
        await last_auth.get_signatures()

        print(authorizations[0].flat_data)
    return borrower


if __name__ == '__main__':
    asyncio.run(get_borrower())
