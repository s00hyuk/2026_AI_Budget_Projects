# 2026년 AI 재정사업 대시보드

> 533개 AI 재정사업의 2026년 예산 구조 시각화 대시보드

## 🔗 데모 링크

**GitHub Pages 배포 후**: `https://<YOUR_USERNAME>.github.io/<REPO_NAME>/`

---

## 🚀 GitHub Pages 배포 방법

### 1단계: 저장소 생성
```bash
# GitHub에서 새 저장소 생성 후
git init
git add index.html README.md
git commit -m "Add AI budget dashboard"
git remote add origin https://github.com/<USERNAME>/<REPO>.git
git push -u origin main
```

### 2단계: GitHub Pages 활성화
1. 저장소 → **Settings** 탭
2. 왼쪽 메뉴 → **Pages**
3. Source: **Deploy from a branch**
4. Branch: **main** / **/ (root)**
5. **Save** 클릭
6. 약 1~2분 후 URL 생성됨

---

## 📊 기능

| 기능 | 설명 |
|------|------|
| 🔍 검색 | 사업명, 소관부처 텍스트 검색 |
| 🔽 필터 | 소관부처 / 분야 / 지원형태 / 신규·계속 필터 |
| ↕️ 정렬 | 테이블 헤더 클릭으로 오름/내림차순 정렬 |
| 📊 차트 | 부처별·분야별 예산 차트, 지원형태 도넛, 연도별 추이 |
| 🔀 생키 | 소관기관 → 분야 → 프로그램 예산 흐름 다이어그램 |
| 📄 페이지네이션 | 50개씩 페이지 분할 |

## 📁 파일 구조

```
index.html    ← 전체 대시보드 (단일 파일, 외부 CDN만 사용)
README.md     ← 배포 가이드
```

## 🛠 기술 스택

- **Chart.js** 4.4 (CDN) — 막대·도넛·라인 차트
- **Plotly.js** 2.27 (CDN) — 생키 다이어그램
- **Vanilla JS** — 필터링·정렬·페이지네이션

---

*데이터 출처: 2026년 AI 재정사업 533개 구조화 추출 (단위: 백만원 → 시각화시 억원 변환)*
