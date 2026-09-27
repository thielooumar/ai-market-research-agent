# My agent: B2B Target Scout & Interview Strategist (B2B企業インタビュー戦略支援エージェント)
One-liner: A conversational agent that helps B2B solution creators prioritize candidate companies across multiple domains, visualize domain overlaps with Venn diagrams, and generate personalized interview outreach and strategy guides.

Tool coverage:
- Memory: ユーザーの自社ソリューション概要・価値提案、過去にインタビューした企業や除外リスト、アウトリーチ文面の好みのトーン（フォーマル/カジュアル/スタートアップ向け）。
- Tools: 企業のIR・問い合わせ窓口・事業内容のWebリサーチ (`search_company_info`)、分野適合度と課題合致度の優先度スコアリング (`score_interview_priority`)、アプローチメール生成 (`generate_email_template`)、インタビュー設計・質問リスト生成 (`generate_interview_guide`)。
- Catalog/UI: 候補企業カタログ（優先度バッジ、該当分野タグ、親和性スコア、窓口リンク等をカード/テーブル表示するA2UI/カスタムUI）。
- Image gen: 複数分野の重複と企業マッピングを可視化するベン図（Venn Diagram）の画像生成・エクスポート。
- Sandbox: Python Sandboxを用いたベン図（matplotlib-venn等）の動的描画、優先度スコア計算、およびMarkdown形式インタビュー設計書のファイル生成・ダウンロード処理。

Core rails (everyone): memory, tools, eval, deploy, frontend
My stretch menu (pick later): A2UI, Code sandbox, Files/Storage (画像・Markdownダウンロード)
First eval question: 「分野: ['FinTech', 'SaaS', 'サプライチェーン'], 候補企業: ['三菱商事', 'マネーフォワード', 'freee', '野村総合研究所'], 提案ソリューション: 'AIを活用したサプライチェーン資金繰り予測・即時ファクタリング基盤' をインプットした際、複数分野の重複企業を正しく抽出し、最優先企業の連絡先・Webリンク、個別打診メール、インタビュー仮説・質問リストを的確に生成できるか？」
