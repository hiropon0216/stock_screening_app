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