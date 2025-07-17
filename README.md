# 📘 Git プロジェクト初期化 & 運用手順（テンプレート）

## 🧱 初回プロジェクト作成時（GitHubと連携するまで）

1. プロジェクトディレクトリを作成
```bash
mkdir your_project_name
cd your_project_name
```

2. 仮想環境を構築
```
python -m venv venv
source venv/bin/activate  # Windowsは .\venv\Scripts\activate
```

3. Gitを初期化
```
git init
```

4. .gitignoreを作成
```
venv/
__pycache__/
*.pyc
.DS_Store
```

5.README.mdの作成
```
touch README.md
```

6.GitHubで新規リポジトリを作成
 - 右上の＋ボタンからNew repositoryを押下
 - 「READMEを初期化」のチェックは外す

7.GitHubとリモート接続
```
git remote add origin https://github.com/yourusername/your_project_name.git
git branch -M main
```

8.最初のコミット&push
```
git add .
git commit -m "Initial commit"
git push -u origin main
```

## 🔁以降の運用（変更を保存するたびに）
1.変更をステージに追加
```
git add .
```

2.コミットする
```
git commit -m "ここに変更内容を書く"
```

3.GitHunへ反映(push)
```
git push
```

# 🚀開発のロードマップ

## 🔷 ステージ 1：スクリーニング機能のコア実装（バックエンド）
🎯 目標：
移動平均線の位置関係からステージ（1〜6）を判定できる関数を作成し、任意の銘柄コードに対して分析できるようにする。

✅ タスク一覧：
 - yfinanceを用いて株価を取得（過去90営業日程度）

 - EMA（5日, 20日, 60日）を ta ライブラリで計算

 - 大循環ステージを判定する関数を実装

-  1銘柄に対してステージを返す処理を作成（例：screening.py）

## 🔷 ステージ 2：バッチスクリーニング機能の追加
🎯 目標：
複数銘柄（例：東証の全銘柄）に対してスクリーニング処理を一括で実行し、結果をCSVやJSONで保存できるようにする。

✅ タスク一覧：
 - 東証上場銘柄コードのリストを用意（CSVなど）

 - 各銘柄に対して大循環分析を適用し、現在のステージを取得

 - ステージでフィルタリング（例：ステージ1のみ抽出）

 - 結果を data/ フォルダ内にCSVで保存

 - 処理を1ファイルにまとめて実行できるスクリプトを作成（例：batch_screening.py）

## 🔷 ステージ 3：API化（FlaskによるWebバックエンド）
🎯 目標：
条件（例：ステージ1だけ、など）を指定して結果を返すAPIをFlaskで実装

✅ タスク一覧：
 - Flaskプロジェクトを作成（main.py）

 - /screening APIを作成（条件に応じてJSON返却）

 - 日付やステージをパラメータで指定できるようにする

 - CSVデータ or DBから読み込んでレスポンスする

 - エラー処理とCORS対策も実装

## 🔷 ステージ 4：フロントエンド（Web UI）構築
🎯 目標：
ユーザーがブラウザで条件（ステージや更新日など）を指定して、結果を表形式で閲覧できるUIを作成

✅ タスク一覧：
 - HTMLテンプレート（templates/index.html）の作成

 - ステージ選択・日付入力フォームの追加（簡単でOK）

 - /screening API を呼び出すJSの作成

 - レスポンスをテーブルで表示（銘柄コード・ステージ・チャートリンク）

 - BootstrapやTailwindなどの軽量CSSフレームワーク導入（任意）

## 🔷 ステージ 5：デプロイと自動実行の整備
🎯 目標：
誰でもネット経由で使えるように公開し、スクリーニング処理も定期的に自動実行できるようにする。

✅ タスク一覧：
 - Render / Railway / Vercel などでFlaskアプリをデプロイ

 - GitHub Actionsで定期的にスクリーニング処理を自動実行（例：毎朝8時）

 - 取得結果（CSV）をGitHub PagesまたはAPIから取得可能にする

## 🔷 ステージ 6：拡張機能の検討（任意）
✅ 候補：
 - TradingViewチャート埋め込み

 - 銘柄の「お気に入り」保存機能（Cookie or DB）

 - スマホUI対応

 - LINE通知 or Slack通知機能

 - ステージの過去推移グラフの表示

 - 利用者用のログイン機能（認証）