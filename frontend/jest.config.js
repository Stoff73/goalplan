export default {
  testEnvironment: 'jsdom',
  transform: {
    '^.+\\.jsx?$': ['@babel/preset-env', '@babel/preset-react'],
  },
  moduleNameMapper: {
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    '^internal-packages-ui$': '<rootDir>/../internal-packages/ui/src',
  },
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.js'],
  testMatch: ['**/__tests__/**/*.[jt]s?(x)', '**/?(*.)+(spec|test).[jt]s?(x)'],
};
