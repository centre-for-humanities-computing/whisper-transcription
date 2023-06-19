import argparse
import json
import glob
import time
import torch
import whisper
import datetime
import os
import csv
import sys
import docx
import shutil
import zipfile
from tqdm import tqdm
from csv2pdf import convert

def get_base_file_name(file_name):
    return os.path.splitext(file_name)[0]

def check_transcription_exists(file_name, folder_path):
    csv_file_name = f"{os.path.dirname(file_name)}/chc_transcribed_interviews/{os.path.basename(get_base_file_name(file_name))}.csv"
    return os.path.isfile(csv_file_name)

def format_results(result):
    return [(time.strftime('%H:%M:%S', time.gmtime(r['start'])), r['text']) for r in result['segments']]

def write_csv(file_path, data):
    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Timestamp', 'Sentence'])
        writer.writerows(data)

def get_audio_files_in_folder(folder_path):
    audio_files = []
    audio_extensions = ['mp3', 'wav', 'flac', 'm4a', 'aac', 'mp4']

    for audio_extension in audio_extensions:
        audio_files.extend(glob.glob(os.path.join(folder_path, f"*.{audio_extension}")))
        audio_files.extend(glob.glob(os.path.join(folder_path, f"*.{audio_extension.upper()}")))
        audio_files.extend(glob.glob(os.path.join(folder_path, f"**/*.{audio_extension}")))
        audio_files.extend(glob.glob(os.path.join(folder_path, f"**/*.{audio_extension.upper()}")))
        
    return audio_files

def unzip_files_in_folder(folder_path):
    for item in os.listdir(folder_path): # iterate through items in dir
        full_item_path = os.path.join(folder_path, item)
        if full_item_path.endswith('.zip'): # check for ".zip" extension
            file_name = os.path.abspath(full_item_path) # get full path of files
            root = os.path.splitext(file_name)[0]  # gets the file name without extension
            if os.path.isdir(root):  # if directory exists, it means the file has been unzipped.
                print(f'{file_name} has already been unzipped')
                continue
            with zipfile.ZipFile(file_name, 'r') as zip_ref:  # open the zip file in read mode
                zip_ref.extractall(folder_path)  # extract file to dir
                print(f'{file_name} unzipped')


        
def create_docx_file(file_name):
    doc = docx.Document()

    with open(file_name, newline='', encoding='utf-8') as f:
        csv_reader = csv.reader(f) 

        csv_headers = next(csv_reader)
        csv_cols = len(csv_headers)

        table = doc.add_table(rows=2, cols=csv_cols)
        hdr_cells = table.rows[0].cells

        for i in range(csv_cols):
            hdr_cells[i].text = csv_headers[i]

        for row in csv_reader:
            row_cells = table.add_row().cells
            for i in range(csv_cols):
                row_cells[i].text = row[i]

    doc.add_page_break()
    docx_name = file_name.replace(".csv", ".docx")
    doc.save(docx_name)

def main(audio_files_path, to_plain_text, to_docx, to_pdf):
    unzip_files_in_folder(audio_files_path)
    files = get_audio_files_in_folder(audio_files_path)
    print(f"The following files will be transcribed: {files}")
    folder_path = f"{audio_files_path}/chc_transcribed_interviews/"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    for file_name in tqdm(files):
        if check_transcription_exists(file_name, folder_path):
            print(f"{file_name} has already been transcribed, skipping.")
            continue
        else:
            print(f"{file_name} starting ...")
            start = time.time()
            try:
                model = whisper.load_model('large')
                result = model.transcribe(file_name)
            except Exception as e:
                with open(f"{folder_path}/errors.txt", "a", encoding='utf-8') as f:
                    f.write(f"{datetime.datetime.now()}: Error with transcribing {file_name}\nError details: {e}\n")

            try:
                text_file_name = get_base_file_name(file_name)
                results_list = format_results(result)
                output_file_name = f"{os.path.dirname(text_file_name)}/chc_transcribed_interviews/{os.path.basename(text_file_name).replace(audio_files_path, '.')}.csv"
                output_dir_path = os.path.dirname(output_file_name)
                if not os.path.exists(output_dir_path):
                    os.makedirs(output_dir_path)
                write_csv(output_file_name, results_list)
            except Exception as e:
                with open(f"{folder_path}/errors.txt", "a", encoding='utf-8') as f:
                    f.write(f"{datetime.datetime.now()}: Error with saving CSV {file_name}\nError details: {e}\n\n")

            if to_plain_text:
                try:
                    plain_text_file_name = f"{os.path.dirname(text_file_name)}/chc_transcribed_interviews/{os.path.basename(text_file_name).replace(audio_files_path, '.')}"
                    output_dir_path = os.path.dirname(plain_text_file_name)
                    if not os.path.exists(output_dir_path):
                        os.makedirs(output_dir_path)
                    with open(f"{plain_text_file_name}.txt", "w", encoding='utf-8') as f:
                        for r in results_list:
                            f.write(f"{r[1]} ")
                except Exception as e:
                    with open(f"{folder_path}/errors.txt", "a", encoding='utf-8') as f:
                        f.write(f"{datetime.datetime.now()}: Error with saving Text file {file_name}\nError details: {e}\n\n")

            if to_docx:
                try:
                    # Convert to docx
                    docx_file_name = f"{os.path.dirname(text_file_name)}/chc_transcribed_interviews/{os.path.basename(text_file_name).replace(audio_files_path, '.')}"
                    output_dir_path = os.path.dirname(docx_file_name)
                    if not os.path.exists(output_dir_path):
                        os.makedirs(output_dir_path)
                    create_docx_file(f"{docx_file_name}.csv")
                except Exception as e:
                    with open(f"{folder_path}/errors.txt", "a", encoding='utf-8') as f:
                        f.write(f"{datetime.datetime.now()}: Error with saving DOCX {docx_file_name}\nError details: {e}\n\n")

            if to_pdf:
                try:
                    # Convert to pdf
                    pdf_file_name = f"{os.path.dirname(text_file_name)}/chc_transcribed_interviews/{os.path.basename(text_file_name).replace(audio_files_path, '.')}"
                    output_dir_path = os.path.dirname(pdf_file_name)
                    if not os.path.exists(output_dir_path):
                        os.makedirs(output_dir_path)
                    convert(f"{pdf_file_name}.csv", f"{pdf_file_name}.pdf", font="./700623/arial.ttf")
                except Exception as e:
                    with open(f"{folder_path}/errors.txt", "a", encoding='utf-8') as f:
                        f.write(f"{datetime.datetime.now()}: Error with saving PDF {pdf_file_name}\nError details: {e}\n\n")
                    
        time_taken = str(datetime.timedelta(seconds = time.time()-start))
    
        print(f"Total time taken for {file_name} was {time_taken}")
    shutil.make_archive(f"{audio_files_path}/chc_transcribed_interviews", 'zip', folder_path)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("audio_files_path", help="Path to the audio files")
    parser.add_argument("--to_plain_text", action="store_true", help="Convert to Plain Textfile")
    parser.add_argument("--to_docx", action="store_true", help="Convert to DOCX")
    parser.add_argument("--to_pdf", action="store_true", help="Convert to PDF")
    args = parser.parse_args()
    main(args.audio_files_path, args.to_plain_text, args.to_docx, args.to_pdf)

