(function() {
    // Read the meta tag
    const meta = document.querySelector('meta[name="theme-settings"]');
    let settings = {};
    if (meta && meta.content) {
        try {
            settings = JSON.parse(meta.content);
        } catch (e) {
            console.error('Failed to parse theme settings', e);
        }
    }

    // Default configuration
    tailwind.config = {
        theme: {
            extend: {
                colors: {
                    brand: settings.primaryColor || '#2563eb',
                    slate: {
                        50: '#f8fafc',
                        100: '#f1f5f9',
                        200: '#e2e8f0',
                        300: '#cbd5e1',
                        400: '#94a3b8',
                        500: '#64748b',
                        600: '#475569',
                        700: '#334155',
                        800: '#1e293b',
                        900: '#0f172a',
                    },
                    blue: {
                        600: '#2563eb',
                    }
                },
                fontFamily: {
                    sans: ['Inter', 'system-ui', 'sans-serif'],
                    arabic: ['Cairo', 'sans-serif'],
                }
            }
        }
    };
})();
