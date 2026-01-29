"""
PRISM-Lite: Streamlit 웹 인터페이스
다관점 사고 파트너 UI

[버전 히스토리]
- Phase 1: 세션 저장, UI 안정화
- Phase 2-A: 관점별 심화 탐색
- Phase 3: 결과 내보내기 (마크다운 다운로드)
- Phase 4: Document Parse API 연동 (문서 업로드)
"""

import streamlit as st
from datetime import datetime
from analyzer import (
    analyze_multi_perspective,
    deep_dive_perspective,
    get_all_perspectives,
    parse_document,
    get_supported_file_types,
    PERSPECTIVES
)

# ============================================================
# 페이지 설정
# ============================================================
st.set_page_config(
    page_title="PRISM-Lite: 다관점 사고 파트너",
    page_icon="🔮",
    layout="wide"
)

# ============================================================
# 세션 상태 초기화
# ============================================================
def init_session_state():
    """세션 상태 초기화"""
    defaults = {
        "user_input": "",
        "last_result": None,
        "last_query": "",
        "is_analyzing": False,
        # Phase 2: 심화 탐색 관련 상태
        "mode": "analysis",  # "analysis" | "deep_dive"
        "selected_perspective": None,
        "deep_dive_result": None,
        "deep_dive_history": [],
        # Phase 4: 문서 업로드 관련 상태
        "extracted_text": None,  # Document Parse로 추출한 텍스트
        "uploaded_file_name": None,  # 업로드된 파일명
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()


# ============================================================
# 헬퍼 함수들
# ============================================================
def set_example(example_text: str):
    """사이드바 예시 클릭 시 입력창에 텍스트 설정"""
    st.session_state.user_input = example_text
    st.session_state.input_area = example_text  # text_area key와 동기화


def reset_to_analysis():
    """분석 모드로 돌아가기"""
    st.session_state.mode = "analysis"
    st.session_state.selected_perspective = None
    st.session_state.deep_dive_result = None
    st.session_state.deep_dive_history = []


def start_new_analysis():
    """새로운 분석 시작 (전체 초기화)"""
    st.session_state.last_result = None
    st.session_state.last_query = ""
    st.session_state.extracted_text = None
    st.session_state.uploaded_file_name = None
    reset_to_analysis()


def select_perspective(perspective_key: str):
    """관점 선택하여 심화 탐색 모드로 전환"""
    st.session_state.mode = "deep_dive"
    st.session_state.selected_perspective = perspective_key
    st.session_state.deep_dive_result = None
    st.session_state.deep_dive_history = []


def run_analysis(query: str):
    """분석 실행 및 결과 저장"""
    st.session_state.is_analyzing = True
    result = analyze_multi_perspective(query)
    st.session_state.last_result = result
    st.session_state.last_query = query
    st.session_state.is_analyzing = False
    reset_to_analysis()


def run_deep_dive(follow_up: str = ""):
    """심화 탐색 실행"""
    result = deep_dive_perspective(
        original_query=st.session_state.last_query,
        perspective_key=st.session_state.selected_perspective,
        previous_analysis=st.session_state.last_result,
        follow_up_question=follow_up,
        conversation_history=st.session_state.deep_dive_history
    )

    if follow_up:
        st.session_state.deep_dive_history.append({"role": "user", "content": follow_up})
    st.session_state.deep_dive_history.append({"role": "assistant", "content": result})

    st.session_state.deep_dive_result = result


# ============================================================
# [Phase 3] 내보내기 함수들
# ============================================================
def generate_export_markdown() -> str:
    """현재 분석 결과를 마크다운 형식으로 생성합니다."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # 입력 소스 표시
    if st.session_state.uploaded_file_name:
        input_source = f"📄 문서: {st.session_state.uploaded_file_name}"
    else:
        input_source = "💬 텍스트 입력"

    md_content = f"""# 🔮 PRISM-Lite 분석 결과

> 생성일시: {now}
> 입력 방식: {input_source}
> Powered by Upstage Solar API

---

## 📋 분석 주제

**{st.session_state.last_query}**

---

## 📊 다관점 분석 결과

{st.session_state.last_result}

"""

    # 심화 탐색 결과가 있으면 추가
    if st.session_state.mode == "deep_dive" and st.session_state.deep_dive_history:
        perspective = PERSPECTIVES.get(st.session_state.selected_perspective, {})
        perspective_name = perspective.get("name", "알 수 없음")
        perspective_emoji = perspective.get("emoji", "🔍")

        md_content += f"""---

## {perspective_emoji} {perspective_name} 심화 탐색

"""
        for i, msg in enumerate(st.session_state.deep_dive_history):
            if msg["role"] == "user":
                md_content += f"### 💬 추가 질문\n\n{msg['content']}\n\n"
            else:
                md_content += f"### 🔮 답변\n\n{msg['content']}\n\n"

    md_content += """---

*이 분석은 PRISM-Lite(다관점 사고 파트너)에 의해 생성되었습니다.*
*AI의 분석은 참고 자료이며, 최종 판단은 사용자의 몫입니다.*
"""

    return md_content


def get_safe_filename() -> str:
    """파일명에 사용할 안전한 문자열 생성"""
    query = st.session_state.last_query[:30]
    safe_query = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in query)
    safe_query = safe_query.strip().replace(' ', '_')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    return f"PRISM_{safe_query}_{timestamp}.md"


# ============================================================
# UI 컴포넌트
# ============================================================

def render_header():
    """헤더 렌더링"""
    st.title("🔮 PRISM-Lite")
    st.subheader("다관점 사고 파트너 (Multi-Perspective Thinking Partner)")

    st.markdown("""
    > **"하나의 답"이 아닌 "가능성의 지도"를 탐색합니다.**

    질문이나 주제를 입력하면, 네 가지 다른 관점에서 분석을 제공합니다.
    - 🔵 **전통적 관점**: 가장 흔하고 검증된 접근
    - 🟢 **실용적 관점**: 즉시 실행 가능한 현실적 접근
    - 🟡 **비판적 관점**: 반대 의견과 고려할 위험
    - 🔴 **창의적 관점**: 비전형적이지만 가치 있는 접근
    """)

    st.divider()


def render_input_section():
    """[Phase 4] 입력 섹션 렌더링 - 탭으로 텍스트/문서 분리"""

    # 탭으로 입력 방식 선택
    tab_text, tab_document = st.tabs(["💬 텍스트 입력", "📄 문서 업로드"])

    # ─────────────────────────────────────────────
    # 탭 1: 텍스트 입력 (기존)
    # ─────────────────────────────────────────────
    with tab_text:
        user_input = st.text_area(
            "탐색하고 싶은 주제나 질문을 입력하세요:",
            value=st.session_state.user_input,
            placeholder="예: '프로젝트 마감이 촉박한데 품질도 유지해야 합니다. 어떻게 해야 할까요?'",
            height=100,
            key="input_area",
            disabled=st.session_state.is_analyzing
        )

        col1, col2 = st.columns([1, 5])

        with col1:
            if st.button(
                "🔍 분석 시작",
                type="primary",
                disabled=st.session_state.is_analyzing,
                use_container_width=True,
                key="analyze_text_btn"
            ):
                if user_input.strip():
                    with st.spinner("다양한 관점에서 분석 중... 🔮"):
                        run_analysis(user_input)
                    st.toast("✨ 분석이 완료되었습니다!", icon="🎉")
                    st.rerun()
                else:
                    st.warning("주제나 질문을 입력해주세요.")

        with col2:
            if st.session_state.last_result:
                if st.button("🔄 새로운 분석", use_container_width=False, key="new_text_btn"):
                    start_new_analysis()
                    st.rerun()

    # ─────────────────────────────────────────────
    # 탭 2: 문서 업로드 (Phase 4)
    # ─────────────────────────────────────────────
    with tab_document:
        st.markdown("""
        📄 **PDF 또는 이미지 파일**을 업로드하면, 문서 내용을 추출하여 다관점 분석을 수행합니다.

        *Upstage Document Parse API를 활용합니다.*
        """)

        uploaded_file = st.file_uploader(
            "파일을 선택하세요",
            type=get_supported_file_types(),
            help="PDF, PNG, JPG 파일을 지원합니다.",
            key="document_uploader"
        )

        if uploaded_file:
            st.caption(f"📎 선택된 파일: **{uploaded_file.name}** ({uploaded_file.size / 1024:.1f} KB)")

            # 텍스트 추출 버튼
            col1, col2 = st.columns([1, 3])

            with col1:
                if st.button("📤 텍스트 추출", type="secondary", use_container_width=True):
                    with st.spinner("문서에서 텍스트 추출 중... 📄"):
                        result = parse_document(uploaded_file)

                    if result["success"]:
                        st.session_state.extracted_text = result["text"]
                        st.session_state.uploaded_file_name = uploaded_file.name
                        st.toast("✅ 텍스트 추출 완료!", icon="📄")
                        st.rerun()
                    else:
                        st.error(f"⚠️ {result['error']}")

            with col2:
                if st.session_state.extracted_text:
                    if st.button("🔄 다른 파일", use_container_width=False):
                        st.session_state.extracted_text = None
                        st.session_state.uploaded_file_name = None
                        st.rerun()

        # 추출된 텍스트 표시 및 분석
        if st.session_state.extracted_text:
            st.divider()
            st.markdown("### 📝 추출된 텍스트")

            # 추출된 텍스트 미리보기 (접을 수 있게)
            with st.expander("추출된 내용 보기", expanded=False):
                st.text_area(
                    "추출된 텍스트",
                    value=st.session_state.extracted_text,
                    height=200,
                    disabled=True,
                    label_visibility="collapsed"
                )

            # 분석할 질문 입력
            st.markdown("### 💭 분석 질문")
            analysis_question = st.text_input(
                "이 문서에 대해 어떤 관점에서 분석할까요?",
                placeholder="예: '이 문서의 핵심 주장을 분석해줘' 또는 '이 기획서의 강점과 약점을 알려줘'",
                key="doc_analysis_question"
            )

            # 기본 질문 제안
            st.caption("💡 질문 예시: '핵심 내용 요약', '주장의 타당성 분석', '개선점 제안'")

            if st.button(
                "🔍 문서 분석 시작",
                type="primary",
                use_container_width=False,
                key="analyze_doc_btn"
            ):
                # 분석할 내용 구성
                if analysis_question.strip():
                    query = f"[문서 분석 요청]\n\n질문: {analysis_question}\n\n문서 내용:\n{st.session_state.extracted_text[:3000]}"
                else:
                    query = f"[문서 분석 요청]\n\n다음 문서의 핵심 내용을 다관점에서 분석해주세요:\n\n{st.session_state.extracted_text[:3000]}"

                with st.spinner("문서를 다양한 관점에서 분석 중... 🔮"):
                    run_analysis(query)
                st.toast("✨ 문서 분석이 완료되었습니다!", icon="🎉")
                st.rerun()


def render_analysis_result():
    """분석 결과 렌더링 (관점별 탐색 버튼 포함)"""
    if not st.session_state.last_result:
        return

    st.divider()

    # 결과 헤더 + 내보내기 버튼
    header_col1, header_col2 = st.columns([4, 1])

    with header_col1:
        st.markdown("## 📊 분석 결과")
        # 입력 소스 표시
        if st.session_state.uploaded_file_name:
            st.caption(f"📄 **문서**: {st.session_state.uploaded_file_name}")
        else:
            # 긴 쿼리는 잘라서 표시
            display_query = st.session_state.last_query[:100]
            if len(st.session_state.last_query) > 100:
                display_query += "..."
            st.caption(f"**분석 주제**: {display_query}")

    with header_col2:
        md_content = generate_export_markdown()
        filename = get_safe_filename()

        st.download_button(
            label="📥 저장하기",
            data=md_content,
            file_name=filename,
            mime="text/markdown",
            help="분석 결과를 마크다운 파일로 다운로드합니다",
            use_container_width=True
        )

    # 전체 결과 표시
    st.markdown(st.session_state.last_result)

    st.divider()

    # 관점별 심화 탐색 버튼
    st.markdown("### 🔍 더 깊이 탐색하기")
    st.caption("관심 있는 관점을 선택하면, 해당 관점에서 더 깊이 있는 탐색을 진행합니다.")

    col1, col2 = st.columns(2)

    perspectives_list = list(PERSPECTIVES.items())

    with col1:
        for key, info in perspectives_list[:2]:
            if st.button(
                f"{info['emoji']} {info['name']} 탐색하기",
                key=f"dive_{key}",
                use_container_width=True
            ):
                select_perspective(key)
                st.rerun()

    with col2:
        for key, info in perspectives_list[2:]:
            if st.button(
                f"{info['emoji']} {info['name']} 탐색하기",
                key=f"dive_{key}",
                use_container_width=True
            ):
                select_perspective(key)
                st.rerun()


def render_deep_dive_mode():
    """심화 탐색 모드 렌더링"""
    perspective = PERSPECTIVES.get(st.session_state.selected_perspective)
    if not perspective:
        return

    st.divider()

    # 헤더 + 내보내기 버튼
    header_col1, header_col2 = st.columns([4, 1])

    with header_col1:
        st.markdown(f"## {perspective['emoji']} {perspective['name']} 심화 탐색")
        if st.session_state.uploaded_file_name:
            st.caption(f"📄 **문서**: {st.session_state.uploaded_file_name}")
        else:
            display_query = st.session_state.last_query[:80]
            if len(st.session_state.last_query) > 80:
                display_query += "..."
            st.caption(f"**원래 주제**: {display_query}")
        st.caption(f"**관점 설명**: {perspective['description']} (전형성: {perspective['typicality']})")

    with header_col2:
        if st.session_state.deep_dive_history:
            md_content = generate_export_markdown()
            filename = get_safe_filename()

            st.download_button(
                label="📥 저장하기",
                data=md_content,
                file_name=filename,
                mime="text/markdown",
                help="분석 결과와 심화 탐색 내용을 마크다운 파일로 다운로드합니다",
                use_container_width=True
            )

    # 네비게이션 버튼
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("← 분석 결과로", use_container_width=True):
            reset_to_analysis()
            st.rerun()
    with col2:
        if st.button("🔄 새 분석", use_container_width=True):
            start_new_analysis()
            st.rerun()

    st.divider()

    # 심화 탐색 결과가 없으면 자동으로 시작
    if not st.session_state.deep_dive_result:
        with st.spinner(f"{perspective['emoji']} {perspective['name']}에서 깊이 탐색 중..."):
            run_deep_dive()
        st.rerun()

    # 대화 히스토리 전체 표시 (후속 질문이 아래로 이어지도록)
    if st.session_state.deep_dive_history:
        for i, msg in enumerate(st.session_state.deep_dive_history):
            if msg["role"] == "user":
                # 사용자의 추가 질문 표시
                st.markdown("**💬 추가 질문:**")
                st.info(msg["content"])
            else:
                # AI 답변 표시
                st.markdown(msg["content"])

            # 메시지 사이 구분선 (마지막 메시지 뒤에는 표시하지 않음)
            if i < len(st.session_state.deep_dive_history) - 1:
                st.divider()

    st.divider()

    # 추가 질문 입력
    st.markdown("### 💬 추가로 궁금한 점이 있으신가요?")

    follow_up = st.text_input(
        "추가 질문을 입력하세요:",
        placeholder=f"예: '{perspective['name']}의 구체적인 실행 방법을 알려주세요'",
        key="follow_up_input"
    )

    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("💬 질문하기", type="primary", use_container_width=True):
            if follow_up.strip():
                with st.spinner("답변 생성 중..."):
                    run_deep_dive(follow_up)
                st.rerun()
            else:
                st.warning("질문을 입력해주세요.")

    # 다른 관점으로 전환 옵션
    st.divider()
    st.markdown("### 🔀 다른 관점도 탐색해보기")

    other_perspectives = {k: v for k, v in PERSPECTIVES.items()
                         if k != st.session_state.selected_perspective}

    cols = st.columns(3)
    for i, (key, info) in enumerate(other_perspectives.items()):
        with cols[i]:
            if st.button(
                f"{info['emoji']} {info['name']}",
                key=f"switch_{key}",
                use_container_width=True
            ):
                select_perspective(key)
                st.rerun()


def render_sidebar():
    """사이드바 렌더링"""
    with st.sidebar:
        st.markdown("### 💡 사용 예시")
        st.caption("클릭하면 입력창에 자동으로 입력됩니다")

        examples = [
            "새로운 언어를 배우고 싶은데 어떤 방법이 좋을까요?",
            "팀 내 갈등을 해결하려면 어떻게 해야 할까요?",
            "AI 기술을 업무에 도입하려고 합니다.",
            "이직을 고민하고 있습니다.",
            "블로그를 시작하려는데 어떤 주제가 좋을까요?"
        ]

        for i, example in enumerate(examples):
            st.button(
                example,
                key=f"example_{i}",
                use_container_width=True,
                on_click=set_example,
                args=(example,)
            )

        st.divider()

        # 현재 상태 표시
        st.markdown("### 📌 현재 상태")

        if st.session_state.mode == "deep_dive":
            perspective = PERSPECTIVES.get(st.session_state.selected_perspective)
            if perspective:
                st.info(f"{perspective['emoji']} **{perspective['name']}** 심화 탐색 중")
                turn_count = len([m for m in st.session_state.deep_dive_history if m["role"] == "assistant"])
                st.caption(f"대화 턴: {turn_count}")
        elif st.session_state.last_result:
            st.success("분석 완료 ✨")
            if st.session_state.uploaded_file_name:
                st.caption(f"📄 {st.session_state.uploaded_file_name}")
            st.caption("관점을 선택해 더 깊이 탐색하거나,\n결과를 저장해보세요!")
        elif st.session_state.extracted_text:
            st.info("📄 텍스트 추출 완료")
            st.caption("분석 질문을 입력하고 시작하세요!")
        else:
            st.info("주제를 입력하거나 문서를 업로드하세요")

        st.divider()

        # 사용 가이드
        st.markdown("### 📖 사용 가이드")
        with st.expander("어떻게 사용하나요?"):
            st.markdown("""
            **방법 1: 텍스트 입력**
            1. 주제/질문 입력 → 분석 시작

            **방법 2: 문서 업로드** 📄
            1. PDF/이미지 업로드
            2. 텍스트 추출
            3. 분석 질문 입력 → 분석 시작

            **공통**
            - 4가지 관점 확인
            - 관심 관점 선택 → 심화 탐색
            - 추가 질문으로 대화 이어가기
            - 저장하기로 결과 다운로드
            """)

        st.divider()

        st.markdown("### ℹ️ About")
        st.markdown("""
        **PRISM-Lite**는 "협력적 사고 프레임워크"의
        간소화된 구현입니다.

        AI를 "답을 주는 도구"가 아닌
        "함께 생각하는 파트너"로 활용합니다.

        ---

        **사용 기술**
        - 🧠 Solar API (다관점 분석)
        - 📄 Document Parse API (문서 추출)

        [🔗 Upstage Console](https://console.upstage.ai/)
        """)


# ============================================================
# 메인 앱 로직
# ============================================================

def main():
    render_header()
    render_input_section()

    # 모드에 따라 다른 UI 표시
    if st.session_state.mode == "deep_dive" and st.session_state.selected_perspective:
        render_deep_dive_mode()
    else:
        render_analysis_result()

    render_sidebar()


if __name__ == "__main__":
    main()
