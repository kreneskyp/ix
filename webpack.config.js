const path = require('path');
const timestamp = new Date().getTime();
const NODE_ENV = process.env.NODE_ENV || 'development'

module.exports = {
  entry: './frontend/index.js',
  context: __dirname,
  mode: NODE_ENV,
  devtool: 'eval-source-map',
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: [
          {
            loader: 'babel-loader',
            options: {
              sourceMap: true,
            },
          },
        ],
      },
      {
        test: /\.css$/,
        use: [
          'style-loader',
          {
            loader: 'css-loader',
            options: {
              sourceMap: true,
            },
          },
          'postcss-loader',
        ],
      },
    ],
  },
  resolve: {
    extensions: ['*', '.js', '.jsx', '.css'],
    modules: [
        path.resolve('/var/app/frontend'),
        'node_modules'
    ],
    aliasFields: ['browser'],
    fallback: {
      path: (() => {
        try {
          return require.resolve('path-browserify');
        } catch (err) {
          return false;
        }
      })(),
    },
  },
  output: {
    path: path.resolve('/var/app/.compiled-static'),
    publicPath: '/static/',
    filename: 'js/[name].js',
    chunkFilename: 'js/[name]-chunk.js?t=${timestamp}',
  },
  plugins: [
  ],
};
