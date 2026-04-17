import os
import logging
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


# pydantic instead of multi-agent, just for lab and single using
class KanjiVocab(BaseModel):
    word: str = Field(description="Từ vựng gốc (Kanji/Kana)")
    reading: str = Field(description="Cách đọc (Furigana/Hiragana)")
    meaning: str = Field(description="Nghĩa tiếng Việt")
    kanji_analysis: str = Field(
        description="Phân tích chi tiết Kanji (gồm những chữ gì, bộ thủ nào, mẹo nhớ chữ này một cách thú vị, bay bổng)"
    )


class Distractor(BaseModel):
    option_summary: str = Field(description="Tóm tắt nội dung của đáp án rác (bẫy)")
    why_wrong: str = Field(
        description="Giải thích phân tích tại sao đây là bẫy. Phân tích dí dỏm, chỉ ra chỗ thí sinh dễ nghe nhầm hoặc bị lừa."
    )


class JLPTAnalysis(BaseModel):
    raw_text: str = Field(
        description="Bản ghi âm tiếng Nhật chuẩn xác, đã dọn rác và ngắt câu rõ ràng."
    )
    translation: str = Field(
        description="Bản dịch tiếng Việt mượt mà, văn phong tự nhiên như phim truyền hình."
    )
    kanji_list: list[KanjiVocab] = Field(
        description="Danh sách 3-5 từ vựng/kanji quan trọng nhất trong bài."
    )
    distractors_analysis: list[Distractor] = Field(
        description="Phân tích các đáp án rác (bẫy) xuất hiện trong bài."
    )
    correct_reasoning: str = Field(
        description="Chốt lại lý do chọn đáp án đúng một cách thuyết phục và truyền cảm hứng."
    )


def analyze_transcript(raw_transcript: str) -> dict:
    logger.info("Bắt đầu đẩy transcript cho Sensei Gemini phân tích...")

    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro", temperature=0.4, api_key=os.getenv("GEMINI_API_KEY")
        )

        structured_llm = llm.with_structured_output(JLPTAnalysis)

        system_prompt = """
        Bạn là một Sensei luyện thi JLPT người Nhật siêu cấp vui tính, tâm lý và truyền cảm hứng.
        Nhiệm vụ của bạn là phân tích đoạn transcript hội thoại Choukai N3.
        
        YÊU CẦU VĂN PHONG:
        - Bay bổng, thú vị, dùng từ ngữ gần gũi với giới trẻ (Gen Z) để học viên không bị buồn ngủ.
        - Tuyệt đối LỊCH SỰ, KHÔNG dùng từ ngữ thô tục hay chửi thề.
        - Khi phân tích bẫy (Trick), hãy đóng vai một thám tử vạch trần cú lừa của đề thi.
        - Khi phân tích Kanji, hãy kể một câu chuyện nhỏ hoặc mẹo nhớ hình ảnh thật sáng tạo.
        - Nếu trong hội thoại không xuất hiện câu hỏi và các đáp án rõ ràng, hãy để mảng distractors_analysis rỗng. Tuyệt đối không tự bịa ra đáp án.
        
        Transcript thô cần phân tích:
        {transcript}
        """

        prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                (
                    "human",
                    "Sensei ơi, hãy phân tích đoạn hội thoại này và trả về JSON theo đúng cấu trúc nhé!",
                ),
            ]
        )

        chain = prompt_template | structured_llm
        result = chain.invoke({"transcript": raw_transcript})

        logger.info("Sensei đã phân tích xong!")
        return result.model_dump()

    except Exception as e:
        logger.error(f"Lỗi khi Gemini phân tích: {e}", exc_info=True)
        raise RuntimeError(f"Analysis failed: {e}")

