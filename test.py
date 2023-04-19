import os

if __name__ == '__main__':
    print("Creating directory...")

    foldername = ".\\Posnetki\\S1"

    if not os.path.exists(foldername):
        os.makedirs(foldername)
        
    print("Folder should be made!")
    