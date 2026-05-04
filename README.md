# 🔥 PC 핫딜 텔레그램 알림봇

hotdeal.zip/PC 에 새 딜이 올라오면 텔레그램으로 즉시 알림!
GitHub Actions로 10분마다 자동 실행 (완전 무료)

---

## 📋 설정 방법

### 1단계: 텔레그램 봇 만들기

1. 텔레그램에서 **@BotFather** 검색 후 시작
2. `/newbot` 입력
3. 봇 이름 입력 (예: `내PC핫딜봇`)
4. **API Token** 복사해두기 (예: `7123456789:AAFxxxxxx`)
5. 만든 봇을 검색해서 **Start** 버튼 클릭

### 2단계: 내 chat_id 알아내기

브라우저에서 아래 URL 접속 (TOKEN 부분 교체):
```
https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
```
봇에게 아무 메시지 보낸 후 접속하면 `"id"` 값이 보임 → 그게 chat_id

### 3단계: GitHub 레포 설정

1. 이 폴더를 GitHub에 **public** 레포로 올리기
2. 레포 → **Settings** → **Secrets and variables** → **Actions**
3. 아래 두 개 Secret 추가:
   - `TELEGRAM_TOKEN` : 1단계에서 받은 봇 토큰
   - `TELEGRAM_CHAT_ID` : 2단계에서 확인한 숫자 ID

### 4단계: Actions 활성화

- 레포 → **Actions** 탭 → 워크플로우 활성화
- **Run workflow** 버튼으로 테스트 실행!

---

## 🕐 실행 주기

기본값: **10분마다** 체크

더 자주 체크하려면 `crawl.yml`에서 cron 수정:
- 5분: `*/5 * * * *`
- 15분: `*/15 * * * *`

> ⚠️ GitHub Actions 무료 플랜은 월 2,000분 제공
> 10분 간격 → 월 약 4,320분 필요 → **유료 플랜 또는 public 레포 사용 권장**
> **Public 레포는 Actions 무제한 무료!**

---

## 📁 파일 구조

```
├── .github/
│   └── workflows/
│       └── crawl.yml      # 스케줄 설정
├── crawler.py             # 크롤러 + 텔레그램 알림
├── seen_deals.json        # 이미 알림 보낸 딜 캐시
└── README.md
```
