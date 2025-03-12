#config.py

#folder to search
root_directory = r"X:\ROOT"
#target main dir
output_main = r"X:\6_REFERENCE"
#file types
#image_type = ('.jpg', '.jpeg','.png')
#video_type = ('.mp4', '.avi', '.mov', '.mpeg','.mkv')
#doc_type = ('.doc','.docx','.xls','.xlsx','.txt')
#pdf_type = ('.pdf')
#compressed_type = ('.zip','.7z','.rar')
#audio_type = ('.mp3', '.waw')

#folder_type = 'img'  # Options: img, imgEx, video, audio, pdf, doc, zip
process = True

folder_type_database = ('imgEx', 'doc', 'audio', 'video', 'pdf',  'zip')  #, 'img')

output_subdirnames = ('output_full','duplicates','corrupted','output_final')

date_formats = [
            '%Y:%m:%d %H:%M:%S',  # Standard Exif format
            '%Y-%m-%d %H:%M:%S',  # Hyphens
            '%Y/%m/%d %H:%M:%S',  # Slashes
            '%Y%m%d%H%M%S',       # Continuous digits
            '%d:%m:%Y %H:%M:%S',  # Day first
            '%Y:%m:%d',           # Date only
            '%Y-%m-%d',           # Date only with hyphens
            '%Y/%m/%d',           # Date only with slashes
            # Add more formats as needed
            ]

#file types
image_typeNoEx = ('.jpg', '.jpeg','.png')
image_type = ('.jpg', '.jpeg','.png', ".gif", '.bmp', '.JPG', '.JPEG', '.tif')
video_type = ('.mp4', '.avi', '.mov', '.mpeg','.mkv','.mts', '.mpg', '.flv', '.3gp', '.wmv')
audio_type = ('.mp3', '.wav','.wma','.amr','.flac','.aac')
pdf_type = ('.pdf')
compressed_type = ('.zip', '.rar')
doc_type = ('.doc','.docx','.xls','.xlsx','.txt', '.html', '.htm', '.ppt','.pptx','.xml','.srt','.csv','.rtf','.odt','.vcf','.epub','.djvu','.gp3','.gp4','.gp5')
