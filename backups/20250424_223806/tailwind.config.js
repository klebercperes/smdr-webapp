/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './smdr/templates/**/*.html',
    './ipecs/templates/**/*.html',
    './blog/templates/**/*.html',
    './smdr/static/js/**/*.js',
    './blog/static/js/**/*.js'
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
} 