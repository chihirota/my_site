module.exports = {
  content: ["templates/**/*.{html, js}", 'node_modules/preline/dist/*.js'],
  theme: {
    extend: {
    },
    letterSpacing: {
      widest: '.50em',
    }
  },
  plugins: [
    require('flowbite/plugin'), require('preline/plugin')
  ],
  darkMode: 'class',
}
