"""Verification script to test updated ADK tools locally."""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from app.tools import (
    generate_target_companies_by_ai,
    get_company_contact_info,
    create_interview_email_draft,
    create_interview_guide_markdown,
)


def run_tests():
    print("=== Testing 1: generate_target_companies_by_ai ===")
    sections = [
        {"domain": "FinTech", "use_case": "中小企業の請求書即時ファクタリング", "solution": "AI与信・自動買取基盤"},
        {"domain": "サプライチェーン", "use_case": "受発注データ統合・在庫可視化", "solution": "SCM資金繰り予測・決済連携"}
    ]

    analysis = generate_target_companies_by_ai(sections)
    print(f"Status: {analysis['status']}")
    print(f"High Priority Count: {analysis['high_priority_count']}")
    print("AI Discovered Target Companies:")
    for comp in analysis["prioritized_companies"]:
        print(f"  [{comp['priority']}] {comp['company_name']} ({comp['company_type']}, Score: {comp['score']}) - Matched: {comp['matched_domains']}")
        print(f"     Reason: {comp['strategic_reason'][:60]}...")
    
    venn_path = analysis["venn_diagram_file_path"]
    print(f"Venn diagram generated at: {venn_path} (exists: {os.path.exists(venn_path)})")
    if os.path.exists(venn_path):
        print(f"Venn diagram size: {os.path.getsize(venn_path)} bytes")

    print("\n=== Testing 2: get_company_contact_info ===")
    contact = get_company_contact_info("マネーフォワード")
    print(f"Company: {contact['company_name']}")
    print(f"Official URL: {contact['official_url']}")
    print(f"Target Depts: {contact['target_departments']}")

    print("\n=== Testing 3: create_interview_email_draft ===")
    email = create_interview_email_draft("マネーフォワード", "AIを活用したサプライチェーン資金繰り予測", "請求書買取")
    print(f"Subject: {email['subject']}")

    print("\n=== Testing 4: create_interview_guide_markdown ===")
    guide = create_interview_guide_markdown("三菱商事", "AIを活用したサプライチェーン資金繰り予測", "受発注データ統合")
    print(f"Guide file: {guide['file_path']} (exists: {os.path.exists(guide['file_path'])})")

    print("\n=== ALL UPDATED TOOL TESTS COMPLETED SUCCESSFULLY ===")


if __name__ == "__main__":
    run_tests()
