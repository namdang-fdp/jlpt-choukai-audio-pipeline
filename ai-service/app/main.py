# app/main.py
import json
import logging
from app.kafka_engine.consumer import get_consumer
from app.kafka_engine.producer import get_producer
from app.services.s3_service import download_s3_uri_to_temp
from app.services.groq_service import transcribe_with_whisper
# from app.agents.workflow import analyze_transcript             # Sẽ mở comment ở Chặng 3

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def process_pipeline(msg):
    try:
        # 0. Parse Message từ Kafka
        data = json.loads(msg.value().decode("utf-8"))
        task_id = data.get("taskId")
        s3_url = data.get("fileUrl")

        logger.info(f"[TASK_ID: {task_id}] Bắt đầu pipeline cho URL: {s3_url}")

        # 1. Download file S3 bằng Boto3
        temp_audio_path = download_s3_uri_to_temp(s3_url)
        logger.info(f"[TASK_ID: {task_id}] Đã kéo file về: {temp_audio_path}")

        # 2. Groq Whisper bóc băng
        raw_transcript = transcribe_with_whisper(temp_audio_path)

        # Chặng 3: Multi-agent phân tích
        # analysis_payload = analyze_transcript(raw_transcript)

        # Chặng 4: Bắn Kafka (Đã chuẩn bị sẵn)
        # ... logic producer ...

    except Exception as e:
        logger.error(f"Gãy pipeline ở task: {e}", exc_info=True)


def main():
    consumer = get_consumer()
    consumer.subscribe(["audio_uploaded"])
    logger.info("AI Worker is up and listening to 'audio_uploaded'...")

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                logger.error(f"Kafka Error: {msg.error()}")
                continue

            process_pipeline(msg)
            # Chỉ commit khi đã qua hết các chặng thành công (hoặc văng lỗi đã được catch)
            consumer.commit(msg)

    except KeyboardInterrupt:
        logger.info("Worker shutting down...")
    finally:
        consumer.close()


if __name__ == "__main__":
    main()
