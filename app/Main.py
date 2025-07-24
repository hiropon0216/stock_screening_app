from flask import Flask, render_template, request
import pandas as pd
import os
import glob

app = Flask(__name__)

def get_latest_csv():
    files = glob.glob("output/screening_result.csv")
    if not files:
        print("CSVファイルが見つかりません。")
        return None
    latest_file = max(files, key=os.path.getctime)
    print(f"最新のCSVファイル: {latest_file}")
    return latest_file

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    selected_stages = []
    selected_markets = []
    price_min = price_max = volume_min = volume_max = None

    csv_path = get_latest_csv()
    if not csv_path or not os.path.exists(csv_path):
        print("CSVファイルが存在しません。画面表示のみします。")
        return render_template("index.html", results=results, selected_stages=selected_stages,
                               selected_markets=selected_markets, price_min=price_min, price_max=price_max,
                               volume_min=volume_min, volume_max=volume_max)

    df = pd.read_csv(csv_path, encoding='utf-8-sig')
    print(f"CSV読み込み完了 件数: {len(df)}")

    if request.method == "POST":
        print("POSTリクエストを受信しました。")
        selected_stages = request.form.getlist("stages")
        selected_markets = request.form.getlist("markets")
        price_min = request.form.get("price_min")
        price_max = request.form.get("price_max")
        volume_min = request.form.get("volume_min")
        volume_max = request.form.get("volume_max")

        print(f"選択ステージ: {selected_stages}")
        print(f"選択市場: {selected_markets}")
        print(f"価格フィルター: min={price_min}, max={price_max}")
        print(f"出来高フィルター: min={volume_min}, max={volume_max}")

        selected_stages_int = list(map(int, selected_stages)) if selected_stages else []
        print(f"整数化した選択ステージ: {selected_stages_int}")

        df_filtered = df.copy()
        print(f"フィルタ前 件数: {len(df_filtered)}")

        # ステージ絞り込み
        if selected_stages_int:
            df_filtered = df_filtered[
                df_filtered["現在のステージ"].apply(
                    lambda x: int(str(x).replace("ステージ", "")) in selected_stages_int
                )
            ]
            print(f"ステージ絞り込み後 件数: {len(df_filtered)}")

        # 市場・商品区分絞り込み
        if selected_markets:
            df_filtered = df_filtered[df_filtered["市場・商品区分"].isin(selected_markets)]
            print(f"市場絞り込み後 件数: {len(df_filtered)}")

        # 終値フィルタ（floatに変換）
        if price_min:
            df_filtered = df_filtered[df_filtered["最新終値"] >= float(price_min)]
            print(f"価格下限フィルタ後 件数: {len(df_filtered)}")
        if price_max:
            df_filtered = df_filtered[df_filtered["最新終値"] <= float(price_max)]
            print(f"価格上限フィルタ後 件数: {len(df_filtered)}")

        # 出来高フィルタ（floatに変換）
        if volume_min:
            df_filtered = df_filtered[df_filtered["最新出来高"] >= float(volume_min)]
            print(f"出来高下限フィルタ後 件数: {len(df_filtered)}")
        if volume_max:
            df_filtered = df_filtered[df_filtered["最新出来高"] <= float(volume_max)]
            print(f"出来高上限フィルタ後 件数: {len(df_filtered)}")

        results = df_filtered.to_dict(orient="records")
        print(f"最終結果 件数: {len(results)}")
    else:
        print("GETリクエスト - 全件表示")
        results = df.to_dict(orient="records")
        print(f"全件 件数: {len(results)}")

    return render_template(
        "index.html",
        results=results,
        selected_stages=[str(s) for s in selected_stages],
        selected_markets=selected_markets,
        price_min=price_min,
        price_max=price_max,
        volume_min=volume_min,
        volume_max=volume_max
    )

if __name__ == "__main__":
    app.run(debug=True)
