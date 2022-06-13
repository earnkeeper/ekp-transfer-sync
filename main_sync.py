
import asyncio
import logging

from decouple import AutoConfig
from ekp_sdk import BaseContainer

from sync.transfer_sync_service import TransferSyncService


class AppContainer(BaseContainer):
    def __init__(self):
        config = AutoConfig('.env')

        super().__init__(config)

        self.transfer_sync_service = TransferSyncService(
            contract_logs_repo=self.contract_logs_repo,
            moralis_api_service=self.moralis_api_service,
            transaction_sync_service=self.transaction_sync_service,
        )


if __name__ == '__main__':
    container = AppContainer()

    logging.basicConfig(level=logging.INFO)

    logging.info("🚀 Application Start")

    loop = asyncio.get_event_loop()

    loop.run_until_complete(
        container.transfer_sync_service.sync_transfers("0x2bad52989afc714c653da8e5c47bf794a8f7b11d")
    )
