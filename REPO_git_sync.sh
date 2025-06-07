#!/bin/bash

REPO_NAME=$(basename "$PWD")
GIT_REMOTE_SSH="git@github.com:MikeVances/${REPO_NAME}.git"

echo "📁 Проект: $REPO_NAME"
echo "🔗 SSH-репозиторий: $GIT_REMOTE_SSH"

# Проверка gh CLI
if ! command -v gh &> /dev/null; then
    echo "❌ Установи GitHub CLI (https://cli.github.com/)"
    exit 1
fi

# Проверка авторизации
if ! gh auth status &> /dev/null; then
    echo "❌ Выполни авторизацию: gh auth login"
    exit 1
fi

# Проверка .git
if [ -d ".git" ]; then
  echo "⚠️ Git уже инициализирован. Прерывание."
  exit 1
fi

# Генерация README.md
if [ ! -f "README.md" ]; then
  echo "# $REPO_NAME" > README.md
  echo "📝 Создан README.md"
fi

# Генерация .gitignore
if [ ! -f ".gitignore" ]; then
cat <<EOL > .gitignore
# Python
__pycache__/
*.pyc
venv/
# macOS
.DS_Store
# VS Code
.vscode/
EOL
  echo "🧹 Создан .gitignore"
fi

# Инициализация git
git init
git add .
git commit -m "🚀 Initial commit for $REPO_NAME"
git branch -M main

# Создание репозитория на GitHub
gh repo create MikeVances/"$REPO_NAME" --private --source=. --remote=origin --push

echo "✅ Проект $REPO_NAME успешно загружен на GitHub!"


##Запукать с помощью
##chmod +x git_sync.sh
##./git_sync.sh





