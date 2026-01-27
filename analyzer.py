"""
PRISM-Lite: 다관점 분석 모듈
Upstage Solar API를 활용한 다관점 사고 파트너

[버전 히스토리]
- Phase 2: 심화 탐색 함수, 대화 히스토리
- Phase 3: 결과 내보내기
- Phase 4: Document Parse API 연동
"""

import os
import requests
from openai import OpenAI
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# Upstage API 클라이언트 설정
client = OpenAI(
    api_key=os.getenv("UPSTAGE_API_KEY"),
    base_url="https://api.upstage.ai/v1/solar"
)

# ============================================================
# 관점 정의
# 💡 각 관점의 메타데이터를 딕셔너리로 관리
# ============================================================
PERSPECTIVES = {
    "traditional": {
        "emoji": "🔵",
        "name": "전통적 관점",
        "typicality": "높음",
        "description": "가장 흔하고 검증된 접근 방식",
        "color": "blue"
    },
    "practical": {
        "emoji": "🟢",
        "name": "실용적 관점",
        "typicality": "중간-높음",
        "description": "즉시 실행 가능하고 현실적인 접근",
        "color": "green"
    },
    "critical": {
        "emoji": "🟡",
        "name": "비판적 관점",
        "typicality": "중간",
        "description": "반대 의견, 우려, 고려해야 할 위험",
        "color": "orange"
    },
    "creative": {
        "emoji": "🔴",
        "name": "창의적 관점",
        "typicality": "낮음",
        "description": "비전형적이지만 가치 있을 수 있는 접근",
        "color": "red"
    }
}

# ============================================================
# 프롬프트 템플릿
# ============================================================

# 다관점 분석 프롬프트 (기존)
MULTI_PERSPECTIVE_PROMPT = """당신은 "다관점 사고 파트너"입니다.

주어진 주제나 질문에 대해 네 가지 관점에서 분석을 제공합니다.
각 관점은 서로 다른 "전형성(얼마나 흔한 접근인가)"을 가집니다.

## 분석 형식

### 🔵 전통적 관점 (전형성: 높음)
가장 흔하고 검증된 접근 방식입니다.
- **핵심 내용**: [이 관점의 주요 주장이나 접근]
- **강점**: [이 관점이 가진 장점]
- **한계**: [이 관점의 제약이나 단점]

### 🟢 실용적 관점 (전형성: 중간-높음)
즉시 실행 가능하고 현실적인 접근입니다.
- **핵심 내용**: [이 관점의 주요 주장이나 접근]
- **강점**: [이 관점이 가진 장점]
- **한계**: [이 관점의 제약이나 단점]

### 🟡 비판적 관점 (전형성: 중간)
반대 의견, 우려, 고려해야 할 위험을 다룹니다.
- **핵심 내용**: [이 관점의 주요 주장이나 접근]
- **강점**: [이 관점이 가진 장점]
- **한계**: [이 관점의 제약이나 단점]

### 🔴 창의적 관점 (전형성: 낮음)
비전형적이지만 가치 있을 수 있는 접근입니다.
- **핵심 내용**: [이 관점의 주요 주장이나 접근]
- **강점**: [이 관점이 가진 장점]
- **한계**: [이 관점의 제약이나 단점]

---

## 사용자의 주제/질문:
{user_input}

위 형식에 맞춰 네 가지 관점에서 분석해주세요.
각 관점이 서로 다른 시각을 제공하도록 하고,
사용자가 다양한 가능성을 탐색할 수 있게 도와주세요."""


# 💡 [Phase 2] 심화 탐색 프롬프트
DEEP_DIVE_PROMPT = """당신은 "다관점 사고 파트너"입니다.

사용자가 이전에 "{original_query}"에 대해 다관점 분석을 받았고,
그 중 **{perspective_name}**에 관심을 보여 더 깊이 탐색하고 싶어합니다.

## 이전 분석 요약
{previous_analysis}

## 현재 선택한 관점
{perspective_emoji} **{perspective_name}** (전형성: {typicality})
{perspective_description}

## 사용자의 추가 질문
{follow_up_question}

---

## 응답 가이드라인

1. **선택한 관점을 중심으로** 깊이 있는 답변을 제공하세요.
2. 구체적인 **예시, 실행 방법, 고려사항**을 포함하세요.
3. 필요하다면 다른 관점과의 **연결점이나 차이점**도 언급하세요.
4. 사용자가 **다음 단계로 나아갈 수 있는 제안**을 포함하세요.

친절하고 협력적인 톤으로, 함께 생각하는 파트너처럼 응답해주세요."""


# 💡 [Phase 2] 관점 선택 시 초기 심화 탐색 프롬프트
INITIAL_DEEP_DIVE_PROMPT = """당신은 "다관점 사고 파트너"입니다.

사용자가 "{original_query}"에 대해 다관점 분석을 받았고,
그 중 **{perspective_name}**을 선택하여 더 깊이 탐색하고 싶어합니다.

## 선택한 관점
{perspective_emoji} **{perspective_name}** (전형성: {typicality})
{perspective_description}

---

## 응답 가이드라인

이 관점에 대해 다음을 제공해주세요:

1. **구체적인 실행 방법**: 이 관점을 실제로 적용하려면 어떻게 해야 할까요?
2. **실제 사례 또는 예시**: 이 접근이 효과적이었던 상황이 있다면?
3. **예상되는 도전과 대응**: 이 방향으로 갈 때 부딪힐 수 있는 어려움은?
4. **다음 단계 제안**: 더 탐색하고 싶다면 어떤 질문을 해볼 수 있을까요?

마지막에 사용자가 추가 질문을 할 수 있도록 열린 자세로 마무리해주세요."""


# ============================================================
# 핵심 함수들
# ============================================================

def analyze_multi_perspective(user_input: str) -> str:
    """
    사용자 입력을 받아 다관점 분석을 수행합니다.
    
    Args:
        user_input: 분석할 주제나 질문
        
    Returns:
        네 가지 관점에서의 분석 결과
    """
    try:
        response = client.chat.completions.create(
            model="solar-pro",
            messages=[
                {
                    "role": "system",
                    "content": "당신은 사용자의 사고를 확장하는 다관점 사고 파트너입니다."
                },
                {
                    "role": "user",
                    "content": MULTI_PERSPECTIVE_PROMPT.format(user_input=user_input)
                }
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        return _handle_error(e)


def deep_dive_perspective(
    original_query: str,
    perspective_key: str,
    previous_analysis: str = "",
    follow_up_question: str = "",
    conversation_history: list = None
) -> str:
    """
    💡 [Phase 2] 특정 관점에 대해 심화 탐색을 수행합니다.
    
    Args:
        original_query: 원래 분석 요청한 주제/질문
        perspective_key: 선택한 관점 키 (traditional, practical, critical, creative)
        previous_analysis: 이전 분석 결과 (선택적)
        follow_up_question: 사용자의 추가 질문 (선택적)
        conversation_history: 이전 대화 히스토리 (선택적)
        
    Returns:
        심화 분석 결과
    """
    # 관점 정보 가져오기
    perspective = PERSPECTIVES.get(perspective_key)
    if not perspective:
        return f"⚠️ 알 수 없는 관점입니다: {perspective_key}"
    
    # 메시지 구성
    messages = [
        {
            "role": "system",
            "content": f"당신은 사용자의 사고를 확장하는 다관점 사고 파트너입니다. 현재 '{perspective['name']}' 관점에서 깊이 있는 탐색을 돕고 있습니다."
        }
    ]
    
    # 대화 히스토리가 있으면 추가
    if conversation_history:
        messages.extend(conversation_history)
    
    # 프롬프트 선택 및 구성
    if follow_up_question:
        # 후속 질문이 있는 경우
        prompt = DEEP_DIVE_PROMPT.format(
            original_query=original_query,
            perspective_name=perspective["name"],
            perspective_emoji=perspective["emoji"],
            typicality=perspective["typicality"],
            perspective_description=perspective["description"],
            previous_analysis=previous_analysis[:1000] if previous_analysis else "(이전 분석 없음)",
            follow_up_question=follow_up_question
        )
    else:
        # 처음 관점을 선택한 경우
        prompt = INITIAL_DEEP_DIVE_PROMPT.format(
            original_query=original_query,
            perspective_name=perspective["name"],
            perspective_emoji=perspective["emoji"],
            typicality=perspective["typicality"],
            perspective_description=perspective["description"]
        )
    
    messages.append({"role": "user", "content": prompt})
    
    try:
        response = client.chat.completions.create(
            model="solar-pro",
            messages=messages,
            temperature=0.7,
            max_tokens=1500
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        return _handle_error(e)


def get_perspective_info(perspective_key: str) -> dict:
    """
    관점 키로 관점 정보를 조회합니다.
    
    Args:
        perspective_key: 관점 키
        
    Returns:
        관점 정보 딕셔너리
    """
    return PERSPECTIVES.get(perspective_key, None)


def get_all_perspectives() -> dict:
    """모든 관점 정보를 반환합니다."""
    return PERSPECTIVES


# ============================================================
# 💡 [Phase 4] Document Parse API 연동
# ============================================================

DOCUMENT_PARSE_URL = "https://api.upstage.ai/v1/document-digitization"

# 지원 파일 형식
SUPPORTED_FILE_TYPES = {
    "pdf": "application/pdf",
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
}


def parse_document(uploaded_file) -> dict:
    """
    💡 [Phase 4] 업로드된 문서에서 텍스트를 추출합니다.
    
    Args:
        uploaded_file: Streamlit UploadedFile 객체
        
    Returns:
        dict: {
            "success": bool,
            "text": str (추출된 텍스트),
            "error": str (에러 메시지, 실패 시)
        }
    """
    api_key = os.getenv("UPSTAGE_API_KEY")
    
    if not api_key:
        return {
            "success": False,
            "text": "",
            "error": "API 키가 설정되지 않았습니다. `.env` 파일을 확인해주세요."
        }
    
    # 파일 확장자 확인
    file_name = uploaded_file.name.lower()
    file_ext = file_name.split('.')[-1] if '.' in file_name else ''
    
    if file_ext not in SUPPORTED_FILE_TYPES:
        return {
            "success": False,
            "text": "",
            "error": f"지원하지 않는 파일 형식입니다: .{file_ext}\n지원 형식: PDF, PNG, JPG"
        }
    
    try:
        # API 호출
        headers = {
            "Authorization": f"Bearer {api_key}"
        }

        files = {
            "document": (uploaded_file.name, uploaded_file.getvalue(), SUPPORTED_FILE_TYPES[file_ext])
        }

        # 새 API 형식에 맞는 data 파라미터 추가
        data = {
            "ocr": "force",
            "model": "document-parse"
        }

        response = requests.post(
            DOCUMENT_PARSE_URL,
            headers=headers,
            files=files,
            data=data
        )
        
        # 응답 확인
        if response.status_code == 200:
            result = response.json()

            # 텍스트 추출 (API 응답 구조에 따라 조정)
            extracted_text = ""

            # 1. content 필드에서 텍스트 추출
            if "content" in result:
                content = result["content"]
                if isinstance(content, dict):
                    # content.html에서 텍스트 추출 (Upstage API 실제 응답 구조)
                    if "html" in content:
                        import re
                        html_text = content["html"]
                        # HTML 태그 제거
                        extracted_text = re.sub(r'<[^>]+>', ' ', html_text)
                        # <br> 태그는 줄바꿈으로
                        extracted_text = extracted_text.replace('<br>', '\n')
                        # 여러 공백을 하나로
                        extracted_text = re.sub(r'[ \t]+', ' ', extracted_text)
                        # 여러 줄바꿈을 하나로
                        extracted_text = re.sub(r'\n+', '\n', extracted_text).strip()
                    elif "text" in content:
                        extracted_text = content["text"]
                    elif "markdown" in content:
                        extracted_text = content["markdown"]
                elif isinstance(content, str):
                    extracted_text = content

            # 2. text 필드 직접 확인
            if not extracted_text and "text" in result:
                extracted_text = result["text"]

            # 3. elements에서 텍스트 추출
            if not extracted_text and "elements" in result:
                texts = []
                for element in result["elements"]:
                    if "text" in element:
                        texts.append(element["text"])
                    # category가 paragraph, heading 등인 경우도 처리
                    if "content" in element:
                        elem_content = element["content"]
                        if isinstance(elem_content, dict) and "text" in elem_content:
                            texts.append(elem_content["text"])
                        elif isinstance(elem_content, str):
                            texts.append(elem_content)
                extracted_text = "\n".join(texts)

            # 4. pages 필드 확인 (Upstage API 응답 구조)
            if not extracted_text and "pages" in result:
                texts = []
                for page in result["pages"]:
                    if "text" in page:
                        texts.append(page["text"])
                    # words에서 텍스트 추출
                    if "words" in page:
                        page_words = []
                        for word in page["words"]:
                            if "text" in word:
                                page_words.append(word["text"])
                        if page_words:
                            texts.append(" ".join(page_words))
                extracted_text = "\n".join(texts)

            # 5. html 필드에서 텍스트 추출
            if not extracted_text and "html" in result:
                import re
                html_text = result["html"]
                # HTML 태그 제거
                extracted_text = re.sub(r'<[^>]+>', ' ', html_text)
                # 여러 공백을 하나로
                extracted_text = re.sub(r'\s+', ' ', extracted_text).strip()

            # 6. markdown 필드 확인
            if not extracted_text and "markdown" in result:
                extracted_text = result["markdown"]

            if extracted_text:
                return {
                    "success": True,
                    "text": extracted_text.strip(),
                    "error": ""
                }
            else:
                # 디버깅을 위해 응답의 키 목록 표시
                available_keys = list(result.keys()) if isinstance(result, dict) else []
                return {
                    "success": False,
                    "text": "",
                    "error": f"문서에서 텍스트를 추출할 수 없습니다. (응답 키: {available_keys})"
                }
        
        elif response.status_code == 401:
            return {
                "success": False,
                "text": "",
                "error": "API 인증 실패. API 키를 확인해주세요."
            }
        
        elif response.status_code == 413:
            return {
                "success": False,
                "text": "",
                "error": "파일 크기가 너무 큽니다. 더 작은 파일을 사용해주세요."
            }
        
        else:
            return {
                "success": False,
                "text": "",
                "error": f"API 오류 (상태 코드: {response.status_code})"
            }
    
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "text": "",
            "error": "요청 시간이 초과되었습니다. 다시 시도해주세요."
        }
    
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "text": "",
            "error": "서버에 연결할 수 없습니다. 인터넷 연결을 확인해주세요."
        }
    
    except Exception as e:
        return {
            "success": False,
            "text": "",
            "error": f"문서 처리 중 오류: {str(e)}"
        }


def get_supported_file_types() -> list:
    """지원하는 파일 확장자 목록을 반환합니다."""
    return list(SUPPORTED_FILE_TYPES.keys())


# ============================================================
# 헬퍼 함수
# ============================================================

def _handle_error(e: Exception) -> str:
    """에러를 사용자 친화적 메시지로 변환합니다."""
    error_message = str(e)
    
    if "api_key" in error_message.lower() or "authentication" in error_message.lower():
        return "⚠️ **API 키 오류**\n\nAPI 키가 설정되지 않았거나 올바르지 않습니다.\n`.env` 파일에 `UPSTAGE_API_KEY`가 올바르게 설정되어 있는지 확인해주세요."
    
    elif "connection" in error_message.lower() or "timeout" in error_message.lower():
        return "⚠️ **연결 오류**\n\n서버에 연결할 수 없습니다. 인터넷 연결을 확인해주세요."
    
    else:
        return f"⚠️ **분석 중 오류가 발생했습니다**\n\n```\n{error_message}\n```\n\n문제가 지속되면 API 키와 네트워크 연결을 확인해주세요."


# ============================================================
# 테스트
# ============================================================
if __name__ == "__main__":
    print("=" * 50)
    print("🔮 PRISM-Lite 분석 모듈 테스트")
    print("=" * 50)
    
    # 테스트 1: 다관점 분석
    print("\n[테스트 1] 다관점 분석")
    test_input = "스타트업에서 AI 기술을 도입하려고 합니다."
    print(f"입력: {test_input}\n")
    # result = analyze_multi_perspective(test_input)
    # print(result)
    print("(API 호출 생략 - 실제 테스트 시 주석 해제)")
    
    # 테스트 2: 심화 탐색
    print("\n[테스트 2] 심화 탐색 (창의적 관점)")
    # deep_result = deep_dive_perspective(
    #     original_query=test_input,
    #     perspective_key="creative"
    # )
    # print(deep_result)
    print("(API 호출 생략 - 실제 테스트 시 주석 해제)")
    
    # 테스트 3: 관점 정보 조회
    print("\n[테스트 3] 관점 정보 조회")
    for key, info in PERSPECTIVES.items():
        print(f"  {info['emoji']} {info['name']} ({key})")
