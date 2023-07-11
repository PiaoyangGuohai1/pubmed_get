import os

# 检测是否存在J_Medline文件
def J_Med_download():
    path = "../data/J_Medline.csv"
    if not os.path.exists(path):
        os.system("wget https://ftp.ncbi.nih.gov/pubmed/J_Medline.txt")

        # 打开txt文件
        with open(path, "r") as file:
            lines = file.readlines()

        # 创建csv文件并写入表头
        with open(path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["JrId", "JournalTitle", "MedAbbr", "ISSN (Print)", "ISSN (Online)", "IsoAbbr", "NlmId"])

            # 解析每个记录并写入数据
            for i in range(1, len(lines)+1, 8):
                jr_id = lines[i].split(":")[1].strip()
                journal_title = lines[i+1].split(":")[1].strip()
                med_abbr = lines[i+2].split(":")[1].strip()
                issn_print = lines[i+3].split(":")[1].strip()
                issn_online = lines[i+4].split(":")[1].strip()
                iso_abbr = lines[i+5].split(":")[1].strip()
                nlm_id = lines[i+6].split(":")[1].strip()

                writer.writerow([jr_id, journal_title, med_abbr, issn_print, issn_online, iso_abbr, nlm_id])
    print("J_Medline文件已经准备好。")