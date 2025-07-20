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

    csv_path = get_latest_csv()
    if not csv_path or not os.path.exists(csv_path):
        return render_template("index.html", results=results, selected_stages=selected_stages)

    df = pd.read_csv(csv_path, encoding='utf-8-sig')

    if request.method == "POST":
        selected_stages = request.form.getlist("stages")  # ✅ 'stages'に修正
        selected_stages_int = list(map(int, selected_stages)) if selected_stages else []

        if selected_stages_int:
            df_filtered = df[df["現在のステージ"].isin(selected_stages_int)]
        else:
            df_filtered = df

        results = df_filtered.to_dict(orient="records")
    else:
        results = df.to_dict(orient="records")

    return render_template(
        "index.html",
        results=results,
        selected_stages=[str(s) for s in selected_stages]  # チェック状態を維持するためにstr化
    )

if __name__ == "__main__":
    app.run(debug=True)
