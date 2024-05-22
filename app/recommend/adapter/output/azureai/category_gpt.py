from openai import AzureOpenAI

from config import config

import logging

# initialize logger
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
log = logging.getLogger(__name__)
categories = "백엔드, 프론트엔드, 인공지능, 데브옵스, 인프라, 웹, 서버, 데이터베이스, 리눅스, 앱 네이티브, " + \
             "플러터, 자바스크립트, 어셈블리, 딥러닝, 머신러닝, 데이터과학, 대외활동, 동아리, 공모전, 해커톤, " + \
             "트러블슈팅, 네트워크, 운영체제, 컴퓨터구조, 알고리즘, 자료구조, 코딩테스트"


class GPTAdapter:

    def __init__(self):
        self.client = AzureOpenAI(
            api_version=config.OPENAI_API_VERSION,
            azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
            api_key=config.AZURE_OPENAI_API_KEY,
        )

    async def extract_category(self, content: str):
        response = self.client.chat.completions.create(
            model=config.OPENAI_DEPLOYMENT_NAME,
            messages=[
                {
                    "role": "system",
                    "content": f"You have to categorize the post into three of the following categories: " + categories
                    + "\nYou have to answer in format 'a,b,c'"
                },
                {
                    "role": "user",
                    "content": content
                },
            ],
            temperature=0.3
        )
        log.info(f"result: {response.choices[0].message.content}")
        return response.choices[0].message.content
