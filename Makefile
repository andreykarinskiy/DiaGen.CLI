.PHONY: help release check-branch check-clean

help:
	@echo "Доступные команды:"
	@echo "  make release      - Создать релиз"

release: check-branch check-clean
	@echo "Создание очередного релиза..."
	cz bump --changelog --yes
	@echo "Новая версия: $$(cz version --project)"
	git push origin main --follow-tags

check-branch:
	@current=$$(git branch --show-current); \
	if [ "$$current" != "main" ]; then \
		echo "Текущая ветка: '$$current', релиз должен создаваться из ветки 'main'!"; \
		exit 1; \
	fi

check-clean:
	@if [ -n "$$(git status --porcelain)" ]; then \
		echo "Рабочий каталог содержит незафиксированные изменения!"; \
		exit 1; \
	fi