// ESM config - vite будет загружен через npx
export default async () => {
  // Динамический импорт плагина
  const react = (await import('@vitejs/plugin-react')).default;

  return {
    plugins: [react()],
    server: {
      host: '0.0.0.0',
      port: 5173,
      proxy: {
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
          cookieDomainRewrite: 'localhost',
          configure: (proxy, _options) => {
            proxy.on('proxyReq', (proxyReq, req, _res) => {
              // Передаем cookies из оригинального запроса
              if (req.headers.cookie) {
                proxyReq.setHeader('Cookie', req.headers.cookie);
              }
            });
          },
        }
      }
    },
    test: {
      environment: 'jsdom',
      globals: true,
      setupFiles: './src/setupTests.ts',
    },
  }
}

