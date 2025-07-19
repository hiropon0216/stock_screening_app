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

## 🔷 ステージ 1：コアスクリーニングエンジンの実装
🎯 目的：
EMA(5, 20, 40)に基づく大循環ステージ（1〜6）分類ロジックを確立

1銘柄の分析 → 複数銘柄への自動適用

✅ タスク：
 yfinanceで株価取得（例：過去90営業日）

 taまたはpandasでEMAを計算

 ステージ判定関数を定義（例：determine_stage()）

 複数銘柄（東証上場銘柄一覧）に対してループ処理

 判定結果をDataFrameに格納し、後でJSON形式で返せるよう整備

## 🔷 ステージ 2：ステージ別データキャッシュ・JSON生成
🎯 目的：
全銘柄の大循環分析を定期実行しておき、結果をAPIで即返せるようにする

✅ タスク：
 スクリーニングバッチ（例：batch_screening.py）作成

 結果を stage_1.json 〜 stage_6.json に分けて保存

 必要に応じて日付付き保存（例：screened_2025-07-17.json）

## 🔷 ステージ 3：Flask APIの実装（ステージ別取得）
🎯 目的：
UIからのステージ選択に応じて、JSONで銘柄リストを返すREST APIを作成

✅ タスク：
 Flaskエンドポイント /api/screening?stage=1 〜 6 を作成

 ステージ番号を受け取り、該当のJSONファイルから結果を返却

 エラーハンドリングとCORS対応を実装

## 🔷 ステージ 4：Web UIの構築（ステージ選択UI）
🎯 目的：
「大循環分析」セクションに、ステージ1〜6のチェックボックスを用意し、該当銘柄を一覧表示する画面を構築

✅ タスク：
 HTML + JSベースのUI（例：Bootstrap + Vanilla JS）

 ステージ1〜6のチェックボックスを配置

 チェックボックスの状態をもとにAPIを呼び出し

 結果を表形式で描画（銘柄コード、銘柄名、ステージなど）

 チャートページ（Yahooなど）へのリンクも追加

## 🔷 ステージ 5：定期スクリーニングの自動実行（GitHub Actionsなど）
🎯 目的：
株価データは日々変わるため、毎日朝に自動スクリーニングを行い、最新結果を保存する。

✅ タスク：
 batch_screening.py をGitHub Actionsやcronで自動実行

 結果ファイルを data/ に更新

 必要に応じて差分チェックやログ出力も整備

## 🔷 ステージ 6：拡張機能の検討（任意）
✅ 候補：
 - TradingViewチャート埋め込み

 - 銘柄の「お気に入り」保存機能（Cookie or DB）

 - スマホUI対応

 - LINE通知 or Slack通知機能

 - ステージの過去推移グラフの表示

 - 利用者用のログイン機能（認証）

 # ✅ フロントエンドのUIイメージ（ざっくり）
```
 [ 移動平均線大循環分析 ]
[✔] ステージ1
[✔] ステージ2
[ ] ステージ3
[ ] ステージ4
[✔] ステージ5
[ ] ステージ6

[ 検索ボタン ]

--- 結果 ---
| 銘柄コード | 銘柄名 | 現在のステージ | チャートリンク |
|------------|--------|----------------|----------------|
| 7203       | トヨタ | ステージ1      | [リンク]       |
| 9984       | ソフトバンクG | ステージ2 | [リンク]       |
```