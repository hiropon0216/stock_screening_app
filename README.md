# Git初期化
git init

# .gitignore作成（以下例）
echo "venv/" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore

# 最初のコミット
git add .
git commit -m "Initial commit: setup project structure and README"

# GitHubと連携（GitHubに新しいリポジトリを作成したら）
git remote add origin https://github.com/yourname/stock_screening_app.git
git branch -M main
git push -u origin main
