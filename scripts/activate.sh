#!/bin/bash

# Определяем цвета
CYAN='\033[0;36m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # Без цвета

# Переходим в корневую директорию
cd "$(dirname "$0")/.."
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Ошибка при переходе в корневую директорию!${NC}"
    exit 1
fi

echo -e "${CYAN}📁 Перешел в корневую директорию: $(pwd)${NC}"

# Запускаем setup.sh
echo -e "${CYAN}⚙️ Запускаю настройку проекта...${NC}"
./scripts/setup.sh
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Ошибка при выполнении setup.sh!${NC}"
    exit 1
fi

# Активируем виртуальное окружение
if [ -d ".venv" ]; then
    echo -e "${CYAN}🔌 Активирую виртуальное окружение...${NC}"
    source .venv/bin/activate
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Ошибка при активации виртуального окружения!${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Виртуальное окружение активировано!${NC}"
else
    echo -e "${RED}❌ Виртуальное окружение не найдено!${NC}"
    exit 1
fi

# Запускаем dev режим
echo -e "${CYAN}🚀 Запускаю dev режим...${NC}"
uv run dev
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Ошибка при запуске dev режима!${NC}"
    exit 1
fi

# echo -e "${GREEN}🎉 Dev режим запущен успешно!${NC}"
