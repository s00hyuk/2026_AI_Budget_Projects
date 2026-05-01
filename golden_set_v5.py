"""
AI 재정사업 RAG 실험용 골든 질의셋 v5
총 120개 질문

[변경 이력 v4 → v5]
- v4 100개 유지
- 신규 20개 추가 (SPARQL 특화 질문)
  - MH: 멀티홉 관계 (8개) — 2단계 이상 관계 traversal
  - RV: 역방향 집합 조회 (6개) — 전체 그래프 역방향 검색
  - CF: 복합 조건 필터 (6개) — AND 다중 조건, Vector RAG 구조적 불가

[핵심 설계 의도]
- v4 100개: 단일 청크 내 조회 → Plain Text / JSON / RDF 비교
- 신규 20개: 멀티홉·역방향·복합필터 → Vector RAG ≈0%, SPARQL ≈90%+
- 이중 구조로 "용도별 다형식 제공" 논지 실증

[평가 방법]
- MH/RV/CF 유형: SPARQL 전용 평가 (Vector RAG와 별도 비교)
- 나머지: soft_em + contains_f1
"""

# v4 기존 100개 import
from golden_set_v4 import GOLDEN_SET as GOLDEN_SET_V4
from golden_set_v4 import normalize, extract_key_tokens, soft_em, contains_f1, evaluate

# ── 신규 20개: SPARQL 특화 질문 ──────────────────────────────
GOLDEN_SET_SPARQL = [

    # ── MH: 멀티홉 관계 (8개) ────────────────────────────────
    # 2단계 이상 관계를 건너야 답할 수 있는 질문
    # Vector RAG: 단일 청크에 없어 구조적으로 답 불가 ≈0%
    # SPARQL: ?시행기관→?사업→?소관기관 traversal ≈90%+
    {
        "id": "MH01",
        "type": "MultiHop",
        "question": "정보통신산업진흥원이 시행기관인 사업들의 소관기관 목록은?",
        "answer": "과학기술정보통신부",
        "source_id": "multiple",
        "difficulty": "hard",
        "eval_method": "SPARQL",
        "sparql_hint": "?s ex:사업시행주체 '정보통신산업진흥원' ; ex:소관 ?org ."
    },
    {
        "id": "MH02",
        "type": "MultiHop",
        "question": "한국지능정보사회진흥원이 시행기관인 사업들이 속한 단위사업명 목록은?",
        "answer": "AI경쟁력강화 스마트화산업기반확충 ICT산업기반확충 데이터산업경쟁력강화",
        "source_id": "multiple",
        "difficulty": "hard",
        "eval_method": "SPARQL",
        "sparql_hint": "?s ex:사업시행주체 '한국지능정보사회진흥원' ; ex:단위사업명 ?unit ."
    },
    {
        "id": "MH03",
        "type": "MultiHop",
        "question": "한국산업은행이 시행기관인 사업들의 소관기관과 지원형태를 나열하시오.",
        "answer": "과학기술정보통신부 출자 금융위원회 출자",
        "source_id": "multiple",
        "difficulty": "hard",
        "eval_method": "SPARQL",
        "sparql_hint": "?s ex:사업시행주체 '한국산업은행' ; ex:소관 ?org ; ex:지원형태_목록 ?type ."
    },
    {
        "id": "MH04",
        "type": "MultiHop",
        "question": "한국에너지공단이 시행하는 사업의 분야명은?",
        "answer": "산업중소기업 에너지",
        "source_id": "0295",
        "difficulty": "medium",
        "eval_method": "SPARQL",
        "sparql_hint": "?s ex:사업시행주체 '한국에너지공단' ; ex:분야명 ?field ."
    },
    {
        "id": "MH05",
        "type": "MultiHop",
        "question": "정보통신기획평가원이 시행기관인 사업들의 2026년 예산 합계는?",
        "answer": "1319012백만원",
        "source_id": "multiple",
        "difficulty": "hard",
        "eval_method": "SPARQL",
        "sparql_hint": "SUM(?budget) WHERE ?s ex:사업시행주체 '정보통신기획평가원' ; ex:예산 ?budget ."
    },
    {
        "id": "MH06",
        "type": "MultiHop",
        "question": "중소기업기술정보진흥원이 시행하는 내역사업들의 소관기관은?",
        "answer": "중소벤처기업부",
        "source_id": "multiple",
        "difficulty": "medium",
        "eval_method": "SPARQL",
        "sparql_hint": "?s ex:사업시행주체 '중소기업기술정보진흥원' ; ex:소관 ?org ."
    },
    {
        "id": "MH07",
        "type": "MultiHop",
        "question": "해양경찰청 소관 사업의 시행기관은?",
        "answer": "해양경찰청",
        "source_id": "0490",
        "difficulty": "medium",
        "eval_method": "SPARQL",
        "sparql_hint": "?s ex:소관 '해양경찰청' ; ex:사업시행주체 ?agent ."
    },
    {
        "id": "MH08",
        "type": "MultiHop",
        "question": "AI컴퓨팅자원활용기반강화 사업의 내역사업 시행기관들이 담당하는 다른 사업명은?",
        "answer": "AI경쟁력강화 데이터산업경쟁력강화",
        "source_id": "multiple",
        "difficulty": "hard",
        "eval_method": "SPARQL",
        "sparql_hint": "정보통신산업진흥원·NIA → 다른 사업 역방향 traversal"
    },

    # ── RV: 역방향 집합 조회 (6개) ───────────────────────────
    # 시행기관·속성으로 역방향 전체 그래프 탐색
    # Vector RAG: 533개 청크 전체 스캔 불가 ≈0%
    # SPARQL: 단일 WHERE 절로 즉시 반환 ≈95%+
    {
        "id": "RV01",
        "type": "Reverse",
        "question": "한국지능정보사회진흥원이 시행기관인 사업은 몇 개인가?",
        "answer": "26개",
        "source_id": "multiple",
        "difficulty": "hard",
        "eval_method": "SPARQL",
        "sparql_hint": "COUNT(?s) WHERE ?s ex:사업시행주체 '한국지능정보사회진흥원' ."
    },
    {
        "id": "RV02",
        "type": "Reverse",
        "question": "정보통신산업진흥원이 시행기관인 사업명을 5개 나열하시오.",
        "answer": "4대지역외AX대전환기획 AI AGENT선도국가사업 AI공간컴퓨팅창업생태계활성화 AI기반뇌발달질환디지털의료기기실증지원 AI반도체실증지원",
        "source_id": "multiple",
        "difficulty": "hard",
        "eval_method": "SPARQL",
        "sparql_hint": "?s ex:사업시행주체 '정보통신산업진흥원' ; ex:사업명 ?name . LIMIT 5"
    },
    {
        "id": "RV03",
        "type": "Reverse",
        "question": "출연 지원형태이면서 고용노동부 소관인 사업 목록은?",
        "answer": "디지털기반고용서비스인프라지원 미래환경변화대응산업안전보건연구개발 사업주직업훈련지원금 일자리정보플랫폼기반AI고용서비스지원 직업능력개발담당자양성 취약노동자지원",
        "source_id": "multiple",
        "difficulty": "hard",
        "eval_method": "SPARQL",
        "sparql_hint": "?s ex:소관 '고용노동부' ; ex:지원형태_목록 '출연' ; ex:사업명 ?name ."
    },
    {
        "id": "RV04",
        "type": "Reverse",
        "question": "2026년 신규 사업 중 지원형태가 출자인 사업 목록은?",
        "answer": "AGI준비프로젝트 AI반도체활용K클라우드기술개발 한국산업은행출자AI컴퓨팅인프라확충 한국에너지기술연구원연구운영비지원 산업은행출자국민성장펀드 광역상수도안정화 국가농업AX플랫폼 중소기업모태조합출자",
        "source_id": "multiple",
        "difficulty": "hard",
        "eval_method": "SPARQL",
        "sparql_hint": "?s ex:사업성격_신규 '1' ; ex:지원형태_목록 ?type . FILTER CONTAINS(?type, '출자')"
    },
    {
        "id": "RV05",
        "type": "Reverse",
        "question": "금융위원회 소관 신규 사업 목록은?",
        "answer": "산업은행출자 국민성장펀드",
        "source_id": "0289",
        "difficulty": "medium",
        "eval_method": "SPARQL",
        "sparql_hint": "?s ex:소관 '금융위원회' ; ex:사업성격_신규 '1' ; ex:사업명 ?name ."
    },
    {
        "id": "RV06",
        "type": "Reverse",
        "question": "사업기간이 3년이면서 신규 사업인 것을 3개 나열하시오.",
        "answer": "개인정보안전활용선도기술개발 신뢰기반AI개인정보보호활용기술개발 AI기반뇌발달질환디지털의료기기실증지원",
        "source_id": "multiple",
        "difficulty": "hard",
        "eval_method": "SPARQL",
        "sparql_hint": "?s ex:사업기간 ?p ; ex:사업성격_신규 '1' . FILTER CONTAINS(?p, '3년') LIMIT 3"
    },

    # ── CF: 복합 조건 필터 (6개) ─────────────────────────────
    # 3개 이상 속성의 AND 조건 — Vector RAG 구조적으로 불가
    # SPARQL: WHERE 절 조합으로 즉시 해결 ≈90%+
    {
        "id": "CF01",
        "type": "ComplexFilter",
        "question": "출연 지원형태이면서 과학기술정보통신부 소관이고 2026년 예산이 1000억원(100000백만원) 이상인 사업은?",
        "answer": "AI컴퓨팅자원활용기반강화 바이오의료기술개발 국가과학기술연구회연구운영비지원 한국과학기술원연구운영비지원 한국과학기술연구원연구운영비지원",
        "source_id": "multiple",
        "difficulty": "hard",
        "eval_method": "SPARQL",
        "sparql_hint": "?s ex:지원형태 '출연' ; ex:소관 '과학기술정보통신부' ; ex:예산 ?b . FILTER(?b >= 100000)"
    },
    {
        "id": "CF02",
        "type": "ComplexFilter",
        "question": "신규 사업이면서 지원형태가 출자인 사업 중 과학기술정보통신부 소관인 것은?",
        "answer": "AGI준비프로젝트 AI반도체활용K클라우드기술개발 한국산업은행출자AI컴퓨팅인프라확충 한국에너지기술연구원연구운영비지원",
        "source_id": "multiple",
        "difficulty": "hard",
        "eval_method": "SPARQL",
        "sparql_hint": "?s ex:사업성격_신규 '1' ; ex:지원형태 ?t ; ex:소관 '과학기술정보통신부' . FILTER CONTAINS(?t,'출자')"
    },
    {
        "id": "CF03",
        "type": "ComplexFilter",
        "question": "중소벤처기업부 소관이면서 계속 사업이고 지원형태가 출연인 사업 목록은?",
        "answer": "ICT융합스마트공장보급확산 데이터인프라구축 스마트제조혁신기술개발사업 중소기업스마트서비스지원 중소벤처행정정보화",
        "source_id": "multiple",
        "difficulty": "hard",
        "eval_method": "SPARQL",
        "sparql_hint": "?s ex:소관 '중소벤처기업부' ; ex:사업성격_계속 '1' ; ex:지원형태 '출연' ."
    },
    {
        "id": "CF04",
        "type": "ComplexFilter",
        "question": "2026년 예산이 전년 대비 감소했으면서 계속 사업이고 과학기술정보통신부 소관인 사업은?",
        "answer": "대학디지털교육역량강화 AI산업육성 스마트빌리지보급확산",
        "source_id": "multiple",
        "difficulty": "hard",
        "eval_method": "SPARQL",
        "sparql_hint": "?s ex:증감 ?d ; ex:사업성격_계속 '1' ; ex:소관 '과학기술정보통신부' . FILTER(?d < 0)"
    },
    {
        "id": "CF05",
        "type": "ComplexFilter",
        "question": "내역사업이 2개 이상이면서 신규 사업인 것을 3개 나열하시오.",
        "answer": "전산운영경비 개인정보안전활용선도기술개발 신뢰기반AI개인정보보호활용기술개발",
        "source_id": "multiple",
        "difficulty": "hard",
        "eval_method": "SPARQL",
        "sparql_hint": "?s ex:내역사업_건수 ?c ; ex:사업성격_신규 '1' . FILTER(?c >= 2) LIMIT 3"
    },
    {
        "id": "CF06",
        "type": "ComplexFilter",
        "question": "일반회계이면서 보조 지원형태이고 2026년 신규 사업인 것 중 예산이 가장 큰 사업은?",
        "answer": "AI기반분산전력망산업육성",
        "source_id": "0295",
        "difficulty": "hard",
        "eval_method": "SPARQL",
        "sparql_hint": "?s ex:회계_기금 '일반회계' ; ex:지원형태 '보조' ; ex:사업성격_신규 '1' ; ex:예산 ?b . ORDER BY DESC(?b) LIMIT 1"
    },
]

# ── 전체 합본 ─────────────────────────────────────────────────
GOLDEN_SET = GOLDEN_SET_V4 + GOLDEN_SET_SPARQL

# ── SPARQL 전용 평가 분리 ─────────────────────────────────────
GOLDEN_SET_VECTOR = [q for q in GOLDEN_SET if q.get('eval_method') != 'SPARQL']
GOLDEN_SET_SPARQL_ONLY = [q for q in GOLDEN_SET if q.get('eval_method') == 'SPARQL']


# ── 통계 요약 ────────────────────────────────────────────────
if __name__ == "__main__":
    from collections import Counter
    types = Counter(q["type"] for q in GOLDEN_SET)
    diffs = Counter(q["difficulty"] for q in GOLDEN_SET)
    evals = Counter(q.get("eval_method","Vector") for q in GOLDEN_SET)
    print(f"총 질문 수: {len(GOLDEN_SET)}개")
    print(f"유형별: { {k:v for k,v in sorted(types.items())} }")
    print(f"난이도: { {k:v for k,v in sorted(diffs.items())} }")
    print(f"평가방식: {dict(evals)}")
    print(f"\nVector RAG 평가용: {len(GOLDEN_SET_VECTOR)}개")
    print(f"SPARQL 전용 평가용: {len(GOLDEN_SET_SPARQL_ONLY)}개")
