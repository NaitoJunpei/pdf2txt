import sys
import os
import glob

### テキストファイルを開き、2回連続で改行があるところでファイルを分割
### ファイル名は元のファイル名の後ろに連番をつける
def split_by_title(text_path):
    temp_text = ""
    filename_count = 0
    first_line = ""
    with open(text_path, "r", encoding="utf-8") as f :
        for line in f:
            ### 2回連続で改行があったらファイルを分割
            ### すなわち、改行のみの行があったらファイルを分割
            if line == "\n":
                if temp_text == "" :
                    continue
                filename_count += 1
                save_text(temp_text, filename_count, text_path, first_line)
                temp_text = ""
                first_line = ""
            else:
                if first_line == "" :
                    first_line = line
                    ### ファイル名に使えない文字を削除
                    first_line = first_line.replace("\n", "").replace(" ", "").replace("　", "").replace(":", "").replace("：", "").replace("?", "").replace("？", "").replace("/", "").replace("\\", "").replace("*", "").replace("\"", "").replace("<", "").replace(">", "").replace("|", "")
                temp_text += line
        ### 最後のファイルを保存
        filename_count += 1
        save_text(temp_text, filename_count, text_path, first_line)
    ### 元のファイルを削除
    os.remove(text_path)

def save_text(text, filename_count, text_path, sub_title=""):
    ### ファイル名を作成
    text_basename = os.path.basename(text_path).replace(".txt", "")
    save_filename = f"{text_basename}_{filename_count:05}_{sub_title}.txt"
    save_directory_path = os.path.dirname(text_path)
    save_path = save_directory_path + os.path.sep + save_filename
    with open(save_path, "w", encoding="utf-8") as f2:
        f2.write(text)

if __name__ == "__main__":
    ### 引数でテキストファイルが保存されたフォルダを指定
    args = sys.argv
    target_path = args[1]
    ### target_path以下のtxtファイルをすべて取得
    text_paths = glob.glob(target_path + os.path.sep + "**" + os.path.sep + "*.txt", recursive=True)
    for text_path in text_paths:
        split_by_title(text_path)