# Инструкция по запуску Frontend

## Проблема
На Windows npm не всегда корректно устанавливает devDependencies в node_modules.

## Решение 1: Использовать npx (рекомендуется)

```powershell
cd C:\dev\trade_accounting\frontend
npx vite --host
```

## Решение 2: Установить vite глобально

```powershell
npm install -g vite@latest
cd C:\dev\trade_accounting\frontend
vite --host
```

## Решение 3: Использовать npm run dev

```powershell
cd C:\dev\trade_accounting\frontend
npm run dev
```

(Скрипт обновлен для использования npx vite)

## Проверка

После запуска откройте в браузере: `http://localhost:5173`

Если видите ошибку про vite.config.ts, попробуйте:
1. Удалить `node_modules/.vite-temp`
2. Перезапустить vite

## Альтернатива: Запуск в Docker (для production)

На production сервере frontend работает в Docker через nginx.
Для локальной разработки рекомендуется использовать один из способов выше.

