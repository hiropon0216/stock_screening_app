from flask import Flask, render_template, request
import pandas as pd
import os
import glob

app = Flask(__name__)

def get_latest_csv():
    files = glob.glob("output/screening_result.csv")
    if not files:
        return None
    latest_file = max(files, key=os.path.getctime)
    return latest_file

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    selected_stages = []
    selected_markets = []

    csv_path = get_latest_csv()
    if not csv_path or not os.path.exists(csv_path):
        return render_template("index.html", results=results, selected_stages=selected_stages, selected_markets=selected_markets)

    df = pd.read_csv(csv_path, encoding='utf-8-sig')

    if request.method == "POST":
        # フォームからの入力取得
        selected_stages = request.form.getlist("stages")
        selected_markets = request.form.getlist("markets")

        # ステージは整数化（空なら空リスト）
        selected_stages_int = list(map(int, selected_stages)) if selected_stages else []

        df_filtered = df

        # ステージ絞り込み
        if selected_stages_int:
            df_filtered = df_filtered[
                df_filtered["現在のステージ"].apply(
                    lambda x: int(str(x).replace("ステージ", "")) in selected_stages_int
                )
            ]

        # 市場・商品区分絞り込み
        if selected_markets:
            df_filtered = df_filtered[df_filtered["市場・商品区分"].isin(selected_markets)]

        results = df_filtered.to_dict(orient="records")
    else:
        results = df.to_dict(orient="records")

    return render_template(
        "index.html",
        results=results,
        selected_stages=[str(s) for s in selected_stages],  # チェック維持用
        selected_markets=selected_markets
    )

if __name__ == "__main__":
    app.run(debug=True)
