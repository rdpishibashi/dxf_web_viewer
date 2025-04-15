import streamlit as st
import ezdxf
import tempfile
import matplotlib.pyplot as plt
from io import BytesIO

st.set_page_config(layout="wide")
st.title("DXF MTEXT Viewer")

st.markdown("""
#### 機能概要
- 複数の DXF ファイルをアップロード（Drag & Drop / Browse）
- 各 DXF から MTEXT のテキスト（フォーマット除去後）を抽出
- テキスト一覧から選択して図形をハイライト
""")

uploaded_files = st.file_uploader("DXFファイルをアップロード", type="dxf", accept_multiple_files=True)

if uploaded_files:
    file_options = {}
    for uploaded_file in uploaded_files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".dxf") as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_file_path = tmp_file.name
        try:
            doc = ezdxf.readfile(tmp_file_path)
            mtexts = []
            for e in doc.modelspace().query("MTEXT"):
                mtexts.append({
                    "handle": e.dxf.handle,
                    "raw": e.dxf.text,
                    "text": e.plain_text(),
                    "pos": (e.dxf.insert.x, e.dxf.insert.y),
                    "doc": doc,
                })
            file_options[uploaded_file.name] = mtexts
        except Exception as e:
            st.error(f"ファイル {uploaded_file.name} の読み込みに失敗しました: {e}")

    selected_file = st.selectbox("ファイル選択", list(file_options.keys()))
    mtexts = file_options[selected_file]

    if mtexts:
        label_map = {f"{m['text']} ({m['handle']})": m for m in mtexts}
        selected_label = st.selectbox("MTEXTを選択", list(label_map.keys()))
        selected_handle = label_map[selected_label]["handle"]

        # 描画
        fig, ax = plt.subplots()
        ax.set_aspect("equal")
        ax.axis("off")
        for m in mtexts:
            x, y = m["pos"]
            color = "red" if m["handle"] == selected_handle else "black"
            ax.text(x, y, m["text"], color=color, fontsize=10)
        st.pyplot(fig)
    else:
        st.warning("このファイルにはMTEXTエンティティが見つかりませんでした。")
