const path = require('path');
const timestamp = new Date().getTime();
const NODE_ENV = process.env.NODE_ENV || 'development'

module.exports = {
  entry: './frontend/index.js',
  context: __dirname,
  mode: NODE_ENV,
  devServer: {
    contentBase: './dist',
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: ['babel-loader'],
      },
    ],
  },
  resolve: {
    extensions: ['*', '.js', '.jsx'],
    modules: [
        path.resolve('/var/app/frontend'),
        'node_modules'
        //path.resolve('/var/npm/node_modules')
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
    sourceMapFilename: 'map/[file].map'
  },
  plugins: [

    //new HtmlWebpackPlugin({
    //  template: 'public/index.html'
    //}),
  ],
  //assets: {
  //  assetsSpace: 100,
  //  excludeAssets: [
  //      /.*-chunk.js.*/,
  //      /.*-chunk.css.*/
  //  ]
  //}
};
