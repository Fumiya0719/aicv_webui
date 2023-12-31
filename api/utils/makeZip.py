import os, subprocess
from time import sleep
def makeZip(imageDirPath, zipSavePath, zipFileName = 'images.zip'):
    zipFilePath = os.path.join(zipSavePath, zipFileName)
    # 先に作成しているzipファイルを削除
    deleteZipFiles(zipSavePath)
    
    # zipコマンドを実行してディレクトリを圧縮
    try:
        subprocess.run(['zip', '-r', zipFilePath, '.'], cwd=imageDirPath, check=True)
        return zipFilePath
    except subprocess.CalledProcessError as e:
        print(f"Error during zip creation: {e}")
        return None
    
# def deleteZip(zipSavePath, zipFileName):
#     zipFilePath = os.path.join(zipSavePath, zipFileName)
#     os.remove(zipFilePath)
    
def deleteZipFiles(zipSavePath):
    for file in os.listdir(zipSavePath):
        if file.endswith('.zip'):
            os.remove(os.path.join(zipSavePath, file))
            
def getZipFileName(zipSavePath):
    sleep(1)
    for file in os.listdir(zipSavePath):
        if file.endswith('.zip'):
            return file
    return None