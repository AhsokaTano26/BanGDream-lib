import type { Config } from 'tailwindcss'
// @ts-ignore
import typography from '@tailwindcss/typography'

export default <Partial<Config>>{
    content: [
        "./components/**/*.{js,vue,ts}",
        "./layouts/**/*.vue",
        "./pages/**/*.vue",
        "./plugins/**/*.{js,ts}",
        "./utils/**/*.{js,ts}",
        "./app.vue",
    ],
    theme: {
        extend: {
            colors: {
                primary: '#5b92e5',
            }
        }
    },
    plugins: [
        typography,
    ],
}