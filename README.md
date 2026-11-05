# Hokutaka | Portfolio

個人サイト [hokutaka.dev](https://hokutaka.dev/) のソースコードです。ポートフォリオ、個人ブログ、更新型の技術調査ノートを掲載しています。

## ページ構成

| ページ | URL | 内容 |
| --- | --- | --- |
| Portfolio | [`/`](https://hokutaka.dev/) | 自己紹介、作品、連絡先 |
| Blog | [`/blog/`](https://hokutaka.dev/blog/) | 制作記録や考えたことのメモ |
| Notes | [`/notes/`](https://hokutaka.dev/notes/) | 動画、広告、生成AIなどの調査内容を継続更新する資料集 |

Notesは完成した解説記事ではなく、必要に応じて内容を検証・更新するためのノートです。調査や文章整理にAIを使う場合があります。

## 技術構成

- **HTML / CSS**：ページの構造と見た目。スタイルは `style.css`。
- **Jekyll / Liquid**：静的サイト生成、共通パーツ、BlogやNotesのページ生成。
- **Markdown**：ブログ投稿と調査ノートの本文。
- **Python 3（標準ライブラリ）**：`build.py` でトップページを単体HTMLにする補助処理。
- **GitHub Actions / GitHub Pages**：ビルド検証と公開。

現状、Node.jsやReactを必要とする構成ではありません。

## 主なディレクトリ・ファイル

```text
.
├── index.html                 # ポートフォリオのトップページ
├── style.css                  # サイト共通スタイル
├── assets/                    # 画像などのアセット
├── _includes/                 # ヘッダー、トップページのパーツ
├── _layouts/                  # 共通、ブログ、調査ノートのレイアウト
├── _posts/                    # Blog記事
├── _notes/                    # Notes記事
├── blog/index.html            # Blog一覧ページ
├── notes/index.html           # Notes一覧ページ
├── _config.yml                # Jekyll設定、URL、collection
├── build.py                   # トップページのみ単体HTML化
├── docs/notes-guide.md
│                              # Notesの更新ガイド
└── .github/workflows/ci.yml   # GitHub Pages向けCI/CD
```

## ローカルでの確認

### サイト全体（Jekyll）

RubyとJekyllの実行環境を用意し、リポジトリ直下で実行します。

```sh
jekyll serve
```

通常は `http://localhost:4000/` で確認できます。インストール方法は [Jekyll公式ドキュメント](https://jekyllrb.com/docs/installation/) を参照してください。

**注意**：このリポジトリにはGemfileがありません。ローカル環境とGitHub Pagesのビルド環境でJekyllのバージョンが異なることがあります。PRではGitHub Actionsによる生成結果も確認してください。

### トップページだけを単体HTML化（Python）

```sh
python3 build.py
```

`dist/index.html` が生成されます。このスクリプトはトップページの `{% include %}` を展開するだけで、**BlogやNotesは生成しません**。別の場所へ配置する場合は `style.css` と `assets/` も必要です。

## コンテンツを更新する

### Blog

`_posts/YYYY-MM-DD-title.md` にMarkdownファイルを追加します。タイトル等はYAMLフロントマターで指定します。Blog一覧はJekyllが生成します。

### Notes

`_notes/*.md` を1テーマ1ファイルとして編集します。文章の追加・訂正時は `updated_at` を更新し、必要に応じて `status`（調査中、要再確認、検証済み等）や更新履歴を変更します。料金、機能、ライセンス等は公式資料と確認日を添える想定です。

詳細は [Notesの更新ガイド](docs/notes-guide.md) を参照してください。

## CI/CD と公開

`.github/workflows/ci.yml` で、PR・`main`へのpush時にPythonのトップページ生成とJekyllの全体ビルドを確認します。`main`へのpushでは、生成されたサイトをGitHub Pagesへデプロイします。

`_site/` や `dist/` は生成物としてGit管理から除外しています。

---

サイトの文書・画像などの権利関係は、それぞれの出典や利用条件に従ってください。
