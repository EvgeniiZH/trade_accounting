# Решение проблемы с Vite на Windows

## Проблема
npm на Windows не устанавливает `vite` в `node_modules`, хотя он указан в `devDependencies`.

## Решение: Использовать Yarn или установить вручную

### Вариант 1: Использовать Yarn (РЕКОМЕНДУЕТСЯ)

```powershell
# Установить Yarn глобально (если еще не установлен)
npm install -g yarn

# В папке frontend
cd C:\dev\trade_accounting\frontend
yarn install
yarn dev
```

### Вариант 2: Установить vite вручную через npm с флагами

```powershell
cd C:\dev\trade_accounting\frontend

# Удалить node_modules
Remove-Item -Recurse -Force node_modules

# Установить vite явно ПЕРВЫМ
npm install vite@5.4.11 --save-dev --no-save

# Затем установить остальные зависимости
npm install --legacy-peer-deps

# Запустить
npm run dev
```

### Вариант 3: Использовать глобальный vite

```powershell
# Установить vite глобально
npm install -g vite@latest

# В папке frontend запустить без конфига
cd C:\dev\trade_accounting\frontend
vite --host --proxy /api http://127.0.0.1:8000
```

### Вариант 4: Временно убрать конфиг

```powershell
cd C:\dev\trade_accounting\frontend

# Переименовать конфиг
Rename-Item vite.config.mjs vite.config.mjs.bak

# Запустить vite без конфига (proxy настроится через параметры)
npx vite@latest --host --proxy /api http://127.0.0.1:8000
```

## Проверка

После успешного запуска вы увидите:
```
VITE vX.X.X  ready in XXX ms

➜  Local:   http://localhost:5173/
```

Откройте `http://localhost:5173` в браузере.

## Если ничего не помогает

Используйте Docker для frontend (как настроено для production):
```powershell
docker compose -f docker-compose.dev.yml up frontend
```

Но это будет медленнее из-за проблем с volumes на Windows.

