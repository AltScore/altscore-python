import httpx


class ReportGeneratorSyncModule:

    def __init__(self, altscore_client):
        self.altscore_client = altscore_client

    def build_headers(self):
        return {"API-KEY": self.altscore_client.api_key}

    def generate(self, report_request: dict) -> str:
        with httpx.Client(base_url=self.altscore_client._borrower_central_base_url) as client:
            response = client.post(
                "/v1/tools/generate-report",
                headers=self.build_headers(),
                json=report_request,
                timeout=120
            )
            if response.status_code == 200:
                return response.json()["url"]
            else:
                raise Exception(response.text)


class ReportGeneratorAsyncModule:

    def __init__(self, altscore_client):
        self.altscore_client = altscore_client

    def build_headers(self):
        return {"API-KEY": self.altscore_client.api_key}

    async def generate(self, report_request: dict) -> str:
        with httpx.AsyncClient(base_url=self.altscore_client._borrower_central_base_url) as client:
            response = await client.post(
                "/v1/tools/generate-report",
                headers=self.build_headers(),
                json=report_request,
                timeout=120
            )
            if response.status_code == 200:
                return response.json()["url"]
            else:
                raise Exception(response.text)
