import math
from ekp_sdk.services import TransactionSyncService, MoralisApiService
from ekp_sdk.db import ContractLogsRepo

TOKEN_TRANSFER_TOPIC = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'

class TransferSyncService:
    def __init__(
        self,
        moralis_api_service: MoralisApiService,
        transaction_sync_service: TransactionSyncService,
        contract_logs_repo: ContractLogsRepo
    ):
        self.contract_logs_repo = contract_logs_repo
        self.moralis_api_service = moralis_api_service
        self.transaction_sync_service = transaction_sync_service
        self.page_size = 1000

    async def sync_transfers(self, address):

        await self.transaction_sync_service.sync_logs(
            address,
            topic0=TOKEN_TRANSFER_TOPIC
        )

        self.decode(self, address)

    def decode(self, address):
        latest_block_number = 0

        address_map = {}

        token_decimals = 18

        while True:
            next_logs = self.contract_logs_repo.find_since_block_number(
                latest_block_number,
                self.page_size,
                source_contract_address=address
            )

            if not len(next_logs):
                break

            for next_log in next_logs:

                data = next_log["data"]
                topics = next_log["topics"]

                if len(topics) < 3 or (topics[0] != TOKEN_TRANSFER_TOPIC):
                    continue

                if len(data) < 66:
                    continue

                from_address = '0x' + topics[1][26:66]
                to_address = '0x' + topics[2][26:66]

                token_raw_value = int(data[2:66], 16)

                token_value = token_raw_value / math.pow(10, token_decimals)

                latest_block_number = next_log.get("blockNumber")

                if from_address not in address_map:
                    address_map[from_address] = {
                        "address": from_address,
                        "value": 0
                    }

                if to_address not in address_map:
                    address_map[to_address] = {
                        "address": to_address,
                        "value": 0
                    }

                address_map[from_address] -= token_value
                address_map[to_address] += token_value

            if len(next_logs) < self.page_size:
                break

        self.__write_csv(address_map)

    def __write_csv(self, records):
        my_file = open(f"addresses.csv", "w")

        my_file.write("address,value\n")

        for record in records:
            my_file.write(f"{record['address']},")
            my_file.write(f"{record['value']},")

        my_file.close()
