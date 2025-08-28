from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'tiktok_comments',
    bootstrap_servers='broker:9092',
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='test-group'
)

for msg in consumer:
    print(f"Offset={msg.offset}, Key={msg.key}, Value={msg.value.decode()}")