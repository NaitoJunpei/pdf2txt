from pdfminer.layout import LTTextBoxHorizontal, LTChar
from pdfminer.high_level import extract_pages
import sys
import os
import glob

def extract_text(pages_obj):
    return_texts = []
    for page_layout in pages_obj:

        lines = []
        positions_x = []
        positions_y = []
        ### タイトルのみ改行ルールを変えるため、タイトルの有無を判定するフラグ
        title_flag = []
        for element in page_layout :
            if isinstance(element, LTTextBoxHorizontal):
                ### 本文
                ### フォント名がMS-Minchoであり、かつadvが-14のものを本文と判定
                if element._objs[0]._objs[0].fontname == 'MS-Mincho' and element._objs[0]._objs[0].adv == -14:
                    text = element.get_text().replace("\n", "")
                    lines.append(text)
                    positions_x.append(element.x0)
                    positions_y.append(element.y0)
                    title_flag.append(False)
                ### タイトル
                ### フォント名がMS-Mincho,Boldのものをタイトルと判定
                elif element._objs[0]._objs[0].fontname == 'MS-Mincho,Bold':
                    text = element.get_text().replace("\n", "")
                    lines.append(text)
                    positions_x.append(element.x0)
                    positions_y.append(element.y0)
                    title_flag.append(True)
                ### その他
                else:
                    pass
            ### 全角スペースが別のオブジェクトとして認識されるため、別個に処理
            elif('_objs' in dir(element)) :
                if isinstance(element._objs[0], LTChar) :
                    if element._objs[0].adv == -14 :
                        text = element.get_text().replace("\n", "").replace("\u3000", "　")
                        lines.append(text)
                        positions_x.append(element.x0)
                        positions_y.append(element.y0)
                        title_flag.append(False)

        ### position_x, position_yの降順でテキストをソート
        if len(positions_x) > 0 :
            zip_lists = zip(positions_x, positions_y, lines, title_flag)
            sorted_zip_lists = sorted(zip_lists, reverse=True)
            positions_x, positions_y, lines, title_flags = zip(*sorted_zip_lists)
            ### 改行のルールを適用
            ### 直前の行で最後が。または」または』または】または）または？または！または・または．で終わる場合は改行
            ### 直前の行がタイトルの行は改行
            ### 行が変わったことは、position_xが変化したことで判定
            break_chars = ["。", "」", "』", "】", "）", "？", "！", "・", "．", "…", "−"]
            position_checker = -1
            line_text = ""
            for i, (position_x, position_y, line, title_flag) in enumerate(sorted_zip_lists):
                if position_checker != position_x:
                    position_checker = position_x
                    if i == 0:
                        ### タイトルの場合は改行する
                        if title_flag :
                            line_text += "\n\n" + line
                            continue
                        line_text += line
                        continue
                    last_char = line_text[-1]
                    if last_char in break_chars:
                        line_text += "\n" + line
                        continue
                    else:
                        ### 直前の行がタイトルの場合は改行
                        if title_flags[i-1] :
                            line_text += "\n" + line
                            continue
                        ### この行がタイトルの場合も改行
                        if title_flag :
                            line_text += "\n\n" + line
                            continue
                line_text += line
            ### ページ区切り
            ### 行終わりと同じ条件で改行
            if len(line_text) > 0 :
                if line_text[-1] in break_chars:
                    line_text += "\n"

            return_texts.append(line_text)
    ### 最初のページと最後のページをスキップ
    return return_texts[1:-1]
                
def open_pdf(pdf_path):
    pages = extract_pages(pdf_path)
    return pages

### テキストファイルとして保存
### 同じフォルダに保存する
def save_txt(texts, pdf_path):
    ### pdfと同じフォルダ/processed/PDFファイル名/PDFファイル名.txt に保存
    pdf_basename = os.path.basename(pdf_path).replace(".pdf", "")
    save_directory_path = os.path.dirname(pdf_path) + os.path.sep + "processed" + os.path.sep + pdf_basename
    ### フォルダがなければ作成
    if not os.path.exists(save_directory_path):
        os.makedirs(save_directory_path)
    save_filename = save_directory_path + os.path.sep + pdf_basename + ".txt"
    with open(save_filename, "w", encoding="utf-8") as f :
        for text in texts:
            f.write(text)

if __name__ == "__main__":
    ### 引数でPDFファイルが保存されたフォルダを指定
    args = sys.argv
    target_path = args[1]
    ### target_path以下のpdfファイルをすべて取得
    pdf_paths = glob.glob(target_path + os.path.sep + "*.pdf")
    for pdf_path in pdf_paths:
        pages = open_pdf(pdf_path)
        texts = extract_text(pages)
        save_txt(texts, pdf_path)
        print(os.path.basename(pdf_path))