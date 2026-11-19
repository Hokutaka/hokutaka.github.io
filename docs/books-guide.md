# Bookshelf

`_templates/book.md` を `_books/好きなファイル名.md` にコピーして編集すると、`/books/` に表示されます。技術書、小説、漫画、画集などジャンルは自由です。

## 項目

```yaml
---
title: "本のタイトル"
author: "著者名"
category: "小説"
owned: true
status: "unread"
---
```

- `title` は必須。書名を入れます。
- `author` は著者名、`category` は自由な分類名です（任意）。
- `owned` は所蔵している場合に `true` を指定します（任意）。
- `status` は `unread`（積読）、`reading`（読書中）、`read`（読了）、`reread`（再読したい）から選べます（任意）。
- 本文は感想やメモとして使えます。空欄でも問題ありません。

本の登録は一冊一ファイルです。所蔵と読了は別々の状態です。書影やISBNは必須ではありません。

`books/index.html` はタイトル順の一覧を生成し、未登録ならその旨を表示します。`_layouts/book.html` は既存Blog/Notesのデザインを流用します。

ビルド確認は `jekyll serve` を使ってください。`build.py` はトップページだけの単体HTML化で、Booksページは生成しません。
