# 🔮 PRISM-Lite

**다관점 사고 파트너 (Multi-Perspective Thinking Partner)**

> "하나의 답"이 아닌 "가능성의 지도"를 탐색합니다.

PRISM-Lite는 AI를 "답을 주는 도구"가 아닌 "함께 생각하는 파트너"로 활용하는 협력적 사고 프레임워크의 간소화된 구현입니다.

프로젝트가 진행됨에따라, API와 연동될 프롬프트를 점점 확장해 완성하는 것을 추구할 것입니다.

> 📖 **프로젝트 배경 및 상세**: [블로그 글 보기][링크](https://blog.naver.com/lguinea/224166893019))

---

## 📁 프로젝트 구조

```
PRISM-Lite/
├── analyzer.py      # 핵심 분석 모듈 (Upstage Solar API 연동)
├── app.py           # Streamlit 웹 인터페이스
├── requirements.txt # Python 패키지 의존성
├── .env.example     # 환경변수 예시 (복사해서 .env로 사용)
└── .gitignore       # Git 무시 파일 목록

PRISM-System Prompt/
├── PRISM-Lite       # API와 연동된 현재 프롬프트
└── PRISM(Perspective-Rich Ideation & Spectrum Mapping).md  # 연동 목표 주요 프롬프트

```

---

## 🚀 빠른 시작 가이드

### Step 1: API 키 발급
1. [Upstage Console](https://console.upstage.ai/)에 가입/로그인합니다
2. API 키를 발급받습니다

### Step 2: 프로젝트 설정

```bash
# 1. 프로젝트 폴더로 이동
cd PRISM-Lite

# 2. 가상환경 생성 및 활성화
python -m venv venv

# Mac/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate

# 3. 패키지 설치
pip install -r requirements.txt
```

### Step 3: API 키 설정

```bash
# .env.example을 복사해서 .env 파일 생성
cp .env.example .env

# .env 파일을 열어서 API 키 입력
# UPSTAGE_API_KEY=up_여기에_실제_키_입력
```

### Step 4: 실행

```bash
streamlit run app.py
```

브라우저에서 자동으로 `http://localhost:8501`이 열립니다!

---

## 🎯 사용 방법

1. **질문 입력**: 탐색하고 싶은 주제나 질문을 입력합니다
2. **분석 시작**: "다관점 분석 시작" 버튼을 클릭합니다
3. **결과 확인**: 네 가지 관점에서의 분석 결과를 확인합니다
   - 🔵 **전통적 관점**: 가장 흔하고 검증된 접근
   - 🟢 **실용적 관점**: 즉시 실행 가능한 현실적 접근
   - 🟡 **비판적 관점**: 반대 의견과 고려할 위험
   - 🔴 **창의적 관점**: 비전형적이지만 가치 있는 접근

### 💡 예시 질문

- "새로운 언어를 배우고 싶은데 어떤 방법이 좋을까요?"
- "팀 내 갈등을 해결하려면 어떻게 해야 할까요?"
- "AI 기술을 업무에 도입하려고 합니다."
- "이직을 고민하고 있습니다."

---

## 🔧 문제 해결

### "API 키 오류" 메시지가 나와요

1. `.env` 파일이 프로젝트 폴더에 있는지 확인하세요
2. API 키가 올바르게 입력되었는지 확인하세요
3. API 키 앞뒤에 불필요한 공백이 없는지 확인하세요

### "연결 오류" 메시지가 나와요

1. 인터넷 연결을 확인하세요
2. VPN을 사용 중이라면 끄고 다시 시도해보세요

### Streamlit이 실행되지 않아요

```bash
# 가상환경이 활성화되어 있는지 확인
# 프롬프트 앞에 (venv)가 보여야 합니다

# 패키지가 설치되어 있는지 확인
pip list | grep streamlit
```

---

## 🔮 확장 가능성

- **문서 기반 분석**: Document Parse API 연동
- **관점별 심화 대화**: 특정 관점 선택 후 깊은 대화
- **분석 히스토리**: 이전 분석 결과 저장 및 비교
- **커스텀 관점**: 사용자 정의 관점 추가

---

## 📝 라이선스

MIT License

---

**Powered by [Upstage Solar API](https://www.upstage.ai/)**
