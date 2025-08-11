#!/bin/bash

# Определяем цвета
CYAN='\033[0;36m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # Без цвета

# Устанавливаем uv если его нет
if ! command -v uv &> /dev/null; then
    echo -e "${CYAN}📥 Устанавливаю uv...${NC}"
    pip install uv
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Ошибка при установке uv!${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ uv установлен!${NC}"
fi

# Проверяем существование проекта
if [ ! -f "pyproject.toml" ]; then
    echo -e "${CYAN}📦 Инициализирую Python проект...${NC}"
    uv init
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Ошибка при инициализации проекта!${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Проект инициализирован!${NC}"
fi

# Проверяем существование .venv
if [ ! -d ".venv" ]; then
    echo -e "${CYAN}🚀 Создаю виртуальное окружение...${NC}"
    uv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Ошибка при создании виртуального окружения!${NC}"
        exit 1
    fi
    echo -e "${GREEN}✨ Виртуальное окружение создано!${NC}"

    echo -e "${CYAN}🔌 Активирую виртуальное окружение...${NC}"
    source .venv/bin/activate
    echo -e "${GREEN}✅ Виртуальное окружение активировано!${NC}"

    echo -e "${CYAN}📦 Устанавливаю зависимости...${NC}"
    uv pip install -e ".[dev]"
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Ошибка при установке зависимостей!${NC}"
        exit 1
    fi
    echo -e "${GREEN}🎉 Установка завершена успешно!${NC}"
else
    echo -e "${CYAN}🔌 Активирую виртуальное окружение...${NC}"
    source .venv/bin/activate
    echo -e "${GREEN}✅ Виртуальное окружение активировано!${NC}"
fi
