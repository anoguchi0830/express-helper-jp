const path = require("path");
const HtmlWebpackPlugin = require("html-webpack-plugin");
const CopyWebpackPlugin = require("copy-webpack-plugin");

const isEnvProduction = process.env.NODE_ENV === "production";

module.exports = {
    mode: isEnvProduction ? "production" : "development",
    devtool: "source-map",

    entry: {
        index: "./src/ui/index.jsx",
        code: "./src/sandbox/code.js"
    },
    experiments: {
        outputModule: true
    },
    output: {
        pathinfo: !isEnvProduction,
        path: path.resolve(__dirname, "dist"),
        module: true,
        filename: "[name].js"
    },
    externalsType: "module",
    externalsPresets: { web: true },
    externals: {
        "add-on-sdk-document-sandbox": "add-on-sdk-document-sandbox",
        "express-document-sdk": "express-document-sdk"
    },
    // パネル Add-on はデータが本体のため 244 KiB 制限は非現実的。
    // 実態に合わせた上限を設定してビルドノイズを排除する。
    performance: {
        hints: isEnvProduction ? "warning" : false,
        maxAssetSize: 2 * 1024 * 1024,
        maxEntrypointSize: 2 * 1024 * 1024
    },
    plugins: [
        new HtmlWebpackPlugin({
            template: "src/index.html",
            scriptLoading: "module",
            excludeChunks: ["code"]
        }),
        new CopyWebpackPlugin({
            patterns: [
                { from: "src/*.json", to: "[name][ext]" },
                {
                    from: "src/ui/data/addons_data.json",
                    to: "data/[name][ext]",
                    // 空フィールドを除去してミニファイ → ファイルサイズを削減
                    transform(content) {
                        const data = JSON.parse(content.toString());
                        data.addons = data.addons.map(addon => {
                            const out = {};
                            for (const [k, v] of Object.entries(addon)) {
                                if (v !== null && v !== "" && !(Array.isArray(v) && v.length === 0)) {
                                    out[k] = v;
                                }
                            }
                            return out;
                        });
                        return JSON.stringify(data);
                    }
                }
            ]
        })
    ],
    module: {
        rules: [
            {
                test: /\.(js|jsx)$/,
                use: ["babel-loader"],
                exclude: /node_modules/
            },
            {
                test: /(\.css)$/,
                use: ["style-loader", "css-loader"]
            }
        ]
    },
    resolve: {
        extensions: [".jsx", ".js", ".css"]
    }
};
