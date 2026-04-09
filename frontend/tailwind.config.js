/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{vue,ts}"],
  theme: {
    extend: {
      colors: {
        bg: "#141418",
        surface: { DEFAULT: "#1a1a1f", elevated: "#24242c" },
        accent: { DEFAULT: "#c9a227", hover: "#d4af37" },
        danger: { DEFAULT: "#6b1c22", deep: "#4a1518" },
      },
      fontFamily: {
        sans: [
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "Roboto",
          "Helvetica Neue",
          "sans-serif",
        ],
        mono: ["ui-monospace", "SFMono-Regular", "Menlo", "monospace"],
      },
      boxShadow: {
        card: "0 8px 32px rgba(0,0,0,0.45)",
      },
    },
  },
  plugins: [],
};
