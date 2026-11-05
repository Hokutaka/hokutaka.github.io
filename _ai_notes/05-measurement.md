---
title: "広告配信と効果測定の基礎"
description: "CPM・CTR・CVR・CPA、UTM、GA4、GTM、A/Bテストを整理する。"
order: 5
reviewed_at: "2026-11-05"
---
## 「何が起きたか」を分けて考える

広告が表示されたこと、クリックされたこと、サイトで行動が起きたこと、商談や契約につながったことは別々の事実。どの段階が計測できるかを整理する。

| 指標 | 基本的な定義 | 計算 |
| --- | --- | --- |
| CPM | 1,000回表示あたりの広告費 | 費用 ÷ 表示数 × 1,000 |
| CTR | 表示に対するクリックの割合 | クリック数 ÷ 表示数 |
| CPC | クリック1回あたりの広告費 | 費用 ÷ クリック数 |
| CVR | クリックに対する成果の割合（例） | CV数 ÷ クリック数 |
| CPA | 成果1件あたりの広告費 | 費用 ÷ CV数 |
| ROAS | 広告費に対する広告由来売上 | 広告由来売上 ÷ 広告費 |

CVRの分母や視聴指標などは計測ツールやレポートで異なる。**比較する前に指標の定義、集計期間、対象を確認する。** 分母がゼロのときは計算できない。

## URLとUTMパラメータ

以下は架空URLの例。URLのパラメータで、流入元・媒体・キャンペーンを区別できる。

```text
https://example.com/?utm_source=example
  &utm_medium=paid_social
  &utm_campaign=introduction
```

UTMを付けたからといって、全ての成果が必ず正確に計測できるわけではない。ブロッカー、同意状態、ブラウザ制限、計測設定などの影響がある。

## 主な計測・レポートツール

| ツール | 用途 | 先に確認する点 |
| --- | --- | --- |
| [Google Analytics 4](https://support.google.com/analytics/) | 流入やイベント、サイト内の行動を分析 | プロパティ、イベント、コンバージョン設定 |
| [Google Tag Manager](https://support.google.com/tagmanager/) | タグの実行条件や管理 | タグの重複、発火条件、同意管理 |
| [Looker Studio](https://lookerstudio.google.com/) | データの可視化・共有 | データソース、集計期間、更新間隔 |
| 各広告媒体の管理画面 | 配信・広告単位の実績 | 指標定義、アトリビューション、審査 |

## A/Bテストを考える

「2つの広告を出した」だけでは検証にならない。先に仮説を決め、比較する条件・主要指標・期間・対象を揃える。予算、配信先、季節性、測定誤差で差が生じ得る。

BtoBでは、問い合わせ数が少なく結論が出しにくい場合がある。少数の結果を過度に一般化しないことが大切。

## データ取り扱い

フォーム内容や個人を識別できる情報を、広告URLや計測イベントにそのまま送信しない。プライバシーポリシー、利用者の同意、媒体のデータ利用規約、必要なアクセス権を確認する。

**未検証事項**：具体的な計測設定・配信先への適合性、個別媒体の最新指標定義。

### 一次情報

- [Google Analytics ヘルプ](https://support.google.com/analytics/)
- [Google Tag Manager ヘルプ](https://support.google.com/tagmanager/)
- [Google 広告ヘルプ](https://support.google.com/google-ads/)
- [Google のキャンペーン URL 作成ガイド](https://support.google.com/analytics/answer/10917952)
