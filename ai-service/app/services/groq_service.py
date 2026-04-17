import os
import logging
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Get API_KEY
client = Groq()


def transcribe_with_whisper(audio_filepath: str) -> str:
    """
    Gửi file âm thanh lên Groq dùng Whisper-large-v3 để bóc băng.
    Trả về string text tiếng Nhật.
    """
    logger.info("Bắt đầu đẩy file lên Groq Whisper...")
    jlpt_primer = (
        "問題１。男の人と女の人が話しています。男の人はこの後、まず何をしますか。"
        "学生、先生、店員、会社員。一番、二番、三番、四番。"
        "では、始めます。ありがとうございます、すみません。"
    )

    try:
        # Mở file dưới dạng binary để đọc
        with open(audio_filepath, "rb") as file:
            # Gọi API Groq
            transcription = client.audio.transcriptions.create(
                file=(audio_filepath, file.read()),
                model="whisper-large-v3",
                prompt=jlpt_primer,
                response_format="json",
                language="ja",
                temperature=0.0,
            )

        result_text = transcription.text
        logger.info("Bóc băng thành công!")

        if os.path.exists(audio_filepath):
            os.remove(audio_filepath)

        return result_text

    except Exception as e:
        logger.error(f"Lỗi khi gọi Groq API: {e}")
        if os.path.exists(audio_filepath):
            os.remove(audio_filepath)
        raise RuntimeError(f"Transcription failed: {e}")
