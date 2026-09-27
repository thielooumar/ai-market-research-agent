"""Root agent definition for B2B Target Scout & Interview Strategist."""

import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

if not os.environ.get("GEMINI_API_KEY"):
    os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")
    os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "keen-optics-296406")
    os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-east1")

from google.adk.agents import Agent

from .a2ui_utils import a2ui_callback
from .tools import (
    generate_target_companies_by_ai,
    analyze_domains_and_priority,
    get_company_contact_info,
    create_interview_email_draft,
    create_interview_guide_markdown,
)

# Attempt importing A2uiSchemaManager from a2ui-agent-sdk; fallback cleanly if not yet installed
try:
    from a2ui.schema.manager import A2uiSchemaManager
    from a2ui.basic_catalog.provider import BasicCatalog

    schema_manager = A2uiSchemaManager(
        version="0.8",
        catalogs=[BasicCatalog.get_config("0.8")],
    )

    instruction = schema_manager.generate_system_prompt(
        role_description=(
            "You are the B2B Target Scout & Interview Strategist. You help solution creators "
            "automatically discover target companies across multiple domain sections (domain, use case, solution overview), "
            "prioritize candidate companies, visualize overlaps with Venn diagrams, and generate interview outreach and guides."
        ),
        workflow_description=(
            "1. When the user provides multiple domain sections (domain, use case, solution overview), call `generate_target_companies_by_ai`.\n"
            "   Return a structured summary of AI-discovered target companies, their priority, and the Venn diagram location.\n"
            "2. When a company is selected or inquired about contacts/links, call `get_company_contact_info`.\n"
            "3. When requested to draft an interview request email, call `create_interview_email_draft`.\n"
            "4. When requested for interview questions or strategy, call `create_interview_guide_markdown`.\n"
            "Always respond with clear, actionable, professional Japanese advice."
        ),
        ui_description=(
            "Keep every surface tiny, clean, and flat: ONE Card > ONE Column > a few Text rows. "
            "Never nest a Card inside a Card. "
            "Use ONLY these components: Card, Column, Row, Text. "
            "Do NOT use Image components. Add a short Text line noting that the Venn diagram is saved to static/venn_diagram.svg. "
            "Display prioritized companies with their priority rank and score using Text components. "
            "No markdown in text; use usageHint ('h1', 'h2', 'body', 'caption') for headings and emphasis. "
            "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in <a2a_datapart_json> tags."
        ),
        include_schema=True,
        include_examples=True,
    )
except ImportError:
    instruction = """
あなたは「B2B Target Scout & Interview Strategist（B2B企業インタビュー戦略支援エージェント）」です。
複数分野・ユースケース・提案ソリューションのセクションを入力とし、Gemini AI機能を用いてターゲット企業リストを発掘・優先度判定・インタビュー戦略策定・ベン図生成を行います。

【提供機能とツールの呼び出し手順】
1. **AI企業発掘 & マルチセクション分析 (要件1, 2, 3, 4, 5)**:
   - ユーザーから「分野」「ユースケース」「提案ソリューション概要」のセクション情報が与えられたら、`generate_target_companies_by_ai` を実行してください。
   - 複数分野の重なり企業を最優先（High）とし、生成されたベン図（Venn Diagram）および企業一覧を案内します。
2. **企業の連絡先・Web窓口取得 (要件6)**:
   - `get_company_contact_info` を実行し、公式Web、IRページ、推奨アプローチ部署を案内します。
3. **アプローチメール文面の生成 (要件7)**:
   - `create_interview_email_draft` を実行し、ユースケース・課題を網羅した個別打診メールを提示します。
4. **インタビュー設計書・質問リスト・Markdown出力 (要件8)**:
   - `create_interview_guide_markdown` を実行し、仮説検証質問項目とアジェンダを整理した Markdown を生成します。

回答はプロフェッショナルなビジネス日本語で行ってください。
"""

model_name = os.environ.get("GEMINI_MODEL", "gemini-3.6-flash")

root_agent = Agent(
    model=model_name,
    name="b2b_interview_strategist",
    instruction=instruction,
    tools=[
        generate_target_companies_by_ai,
        analyze_domains_and_priority,
        get_company_contact_info,
        create_interview_email_draft,
        create_interview_guide_markdown,
    ],
    after_model_callback=a2ui_callback,
)
