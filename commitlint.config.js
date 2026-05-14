module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'header-max-length': [2, 'always', 100],
    'subject-case': [2, 'never', ['start-case', 'pascal-case', 'upper-case']],
    // Custom rule to encourage Linear ID prefix
    'header-pattern': [2, 'always', /^\[KIM-\d+\] .+/],
  },
  parserPreset: {
    parserOpts: {
      headerPattern: /^\[KIM-(\d+)\] (\w+)(?:\(([^)]+)\))?: (.*)$/,
      headerCorrespondence: ['linearId', 'type', 'scope', 'subject'],
    },
  },
};