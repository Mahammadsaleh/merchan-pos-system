const path = require('path');

module.exports = {
    mode: 'development',
    entry: './path/to/your/main.js',
    output: {
        filename: 'bundle.js',
        path: path.resolve(__dirname, 'dist'),
    },
};
