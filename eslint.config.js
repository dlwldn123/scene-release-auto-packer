const globals = require("globals");

module.exports = [
  {
    files: ["**/*.{js,jsx,ts,tsx}"],
    ignores: ["node_modules/**"],
    languageOptions: {
      globals: globals.browser,
      sourceType: "module",
    },
    rules: {},
  },
];
