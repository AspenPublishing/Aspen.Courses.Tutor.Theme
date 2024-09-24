module.exports = {
  important: true,
  content: [
    '../**/templates/*.html',
    '../**/templates/**/*.html'
  ],
  theme: {
    extend: {
      colors: {
        indigoPrimary: '#bf2d2e',
        indigoSecondary: '#d6ae75',
        indigoDark: '#110906',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}