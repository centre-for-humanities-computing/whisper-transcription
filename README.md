## Instructions on transcribing audio files

1. Make sure the data is on uCloud
2. Create an instance using JupyterLab 3.6.1 from the "Apps" tab on the lefthand-side panel
    - Give your instance a name (where it says job name)
    - Choose hours (this should roughly correspond to the number of hours of audio you have)
    - Choose the largest machine type (u1-standard-64 or u1-standard-32)
    - Scroll down to where it says "Select folders to use" and click the "Add folder" button
    - In the second dropdown select the "tools" folder and click the "Use this folder" button in the top righthand corner
    - Click "Add folder" again and select your folder from the second drop down then click the "Use this folder" button.
    - At this point you should have two folders that will be loaded: tools and the folder where your audio files are located.
    - In the top righthand corner, click on the button "Submit"
    - It will say "Your job is being prepared"
3. Click "open terminal" and run the following command where <folder_name> is the name of the folder. This will create csv files containing all the transcriptions
    - ./700623/transcribe.sh ./<folder_name>/data
4. If you also want docx files you can run the following command
    - ./700623/transcribe.sh ./<folder_name>/data --to_plain_text
5. If you also want docx files you can run the following command
    - ./700623/transcribe.sh ./<folder_name>/data --to_plain_text --to_docx
6. If you want docx and pdf files in addition to the csv then you can run the following:
    - ./700623/transcribe.sh ./<folder_name>/data --to_plain_text --to_docx --to_pdf