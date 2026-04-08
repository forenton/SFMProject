from bson import timestamp
from pymongo import MongoClient
from os import getenv
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

host=getenv('MONGO_HOST'),
port=int(getenv('MONGO_PORT'))



class LogService:
    def __init__(self, host=host, port=port, db_name='sfmshop'):
        self.client = MongoClient(
            host=host,
            port=int(port)
        )
        self.db = self.client[db_name]
        self.logs_collection = self.db["logs"]

    def save_log(self, log_data):
        if 'timestamp' not in log_data:
            log_data['timestamp'] = datetime.now()
        result = self.logs_collection.insert_one(log_data)
        return result.inserted_id

    def get_logs_by_type(self, log_type):
        logs = self.logs_collection.find({"type": log_type})
        return list(logs)

    def get_logs_by_status(self, status):
        logs = self.logs_collection.find({"status_code": status})
        return list(logs)

    def get_logs_between_two_dates(self, start_date, end_date):
        logs = self.logs_collection.find({"timestamp": {"$gte": start_date, "$lte": end_date}})
        return list(logs)

    def get_log_by_ip_address(self, ip_address):
        logs = self.logs_collection.find({"ip_address": ip_address})
        return list(logs)

    def get_count_logs_by_type(self):
        pipeline = [{"$group": {"_id": "$type","count": {"$sum": 1}}}]
        result = self.db.logs.aggregate(pipeline)
        output_list = [{"type": doc["_id"], "count": doc["count"]} for doc in list(result)]
        return output_list

    def get_count_logs_by_status_code(self):
        pipeline = [{"$group": {"_id": "$status_code","count": {"$sum": 1}}}]
        result = self.db.logs.aggregate(pipeline)
        output_list = [{"status_code": doc["_id"], "count": doc["count"]} for doc in list(result)]
        return output_list

    def get_count_logs_by_date(self, start_date, end_date):

        pipeline = [{"$match": {"timestamp": {"$gte": start_date, "$lte": end_date}}},
                    {"$group": {"_id": 0, "count": {"$sum": 1}}}]
        result = self.db.logs.aggregate(pipeline)
        result_str = f"Логов с {start_date} по {end_date}: {list(result)[0]['count']}"
        return result_str


if __name__ == '__main__':
    log_service = LogService()
    log = {
        "type": "error",
        "message": "Ошибка подключения к БД",
        "timestamp": "2026-01-15 10:30:00",
        "stack_trace": "...",
        'ip_address': '256.0.0.1',
        'status_code': 402
    }
    log_id = log_service.save_log(log)
    print(f"Лог сохранен с ID: {log_id}")
    print(log_service.get_logs_by_type("error"))
    print(log_service.get_logs_by_status(500))
    print(log_service.get_count_logs_by_date('2025-01-15', '2026-01-16'))
    # print(get_log_by_ip_address('256.0.0.1'))

