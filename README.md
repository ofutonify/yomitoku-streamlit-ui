# Yomitoku Streamlit UI

StreamlitベースのYomitoku OCR WebインターフェースUI

## 前提条件

このUIを使用するには、事前に**Yomitoku**がインストールされている必要があります。

- [Yomitoku](https://github.com/kotaro-kinoshita/yomitoku) - OCRエンジン本体

Yomitokuのインストール方法は、上記リポジトリのREADMEを参照してください。

## インストール

```bash
# 依存関係のインストール
pip install -r requirements.txt
```

## 起動方法

```bash
streamlit run app.py
```

ブラウザで自動的に開かない場合は、ターミナルに表示されるURLにアクセスしてください（通常は `http://localhost:8501`）。

## 使い方

### 1. 画像の入力

以下の2つの方法で画像を入力できます：

- **ファイルアップロード**: ドラッグ&ドロップまたはファイル選択
- **クリップボード貼り付け**: スクリーンショットなどを直接貼り付け

対応形式: PNG, JPG, JPEG, PDF, TIFF, BMP

### 2. 出力形式の選択

処理結果の出力形式を選択します：

- **Markdown** (デフォルト)
- **JSON**
- **HTML**
- **CSV**

### 3. OCR実行

「🚀 Execute Yomitoku」ボタンをクリックして処理を開始します。

### 4. 結果の確認とダウンロード

右カラムに処理結果が表示されます。結果はダウンロードボタンから保存できます。

## 機能

- 画像アップロード/クリップボード貼り付け対応
- 複数の出力形式（Markdown, JSON, HTML, CSV）
- リアルタイムプレビュー
- 処理進捗表示
- 結果のダウンロード

## 詳細なドキュメント

より詳細な使用方法やトラブルシューティングについては、[STREAMLIT_UI.md](STREAMLIT_UI.md)を参照してください。

## ライセンス

このプロジェクトのライセンスについては、元のYomitokuプロジェクトに準拠します。
