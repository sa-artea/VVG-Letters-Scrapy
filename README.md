#  Vincent Van Gogh Gallery Scrapper

Repositorio para trabajar modelos de ML e AI para la obra artistica de Vinvent VanGogh

# **ML-ProMMC**
This is a Machine Learning Technique project for the digital archive of the colombian poet Maria Mercedes Carranza (MMC).
Originaly developed as a part of the final project of the class Machine Learning Techniques at Universidad de los Andes (Uniandes) in 2019-20.

The code has been refactored and its comentaries extended to be part of the presentation of the Rio 2020/2021 Digital Humanities Conference.
***

## **Project Structure**
**LICENCE:** Project licence description.

**README:** Project general description.

**PROJECT STRUCTURE:**
* _\\Notebooks\\:_ Folder where the project's jupyter notebooks are stored
    * _\\Prepro\\:_ Folder with the notebooks for the extraction and preprocessing of the data.
        * _documentProcessing.ipynb:_ PDF 2 TXT jupyter script. 
        * _dataProcessing.ipynb:_ Data regularization, normalization and word2vec script.
    * _\\Models\\:_ Folder with the notebooks for the training and optimization of the ML models.
* _\\Lib\\:_ Common root library for the project's code.
    * _\\Files\\:_ Folder with functionalities to recover and adjust training data.
        * _IO.py:_ Class implemeting the functionalities to transform PDF into TXT this include (PDF 2 RGB_IMG, RGB_IMG 2 B&W_IMG, Image adjustments (contrast, brightness and noise) plus B&W_IMG 2 TXT).
    * _\\Prep\\:_ Folder with functionalities to create and adjust training data.
        * _Groundwork.py:_ Class implementing the functionalities to organize, clean, regularize, normalize and format training data.
    * _\\ML\\:_ Folder with the definition for the ML models.
        * _SVM.py:_ Class implementing the Support Vector Machine (SVM) model to train.
        * _CNN.py:_ Class implementing the Convolutional Neural Network (CNN) model to train.
* _\\Data\\_:
    * _\\pdf\\:_ Folder containing the original training files.
    * _\\img\\:_ Folder containing the training files in *.jpg format.
    * _\\filter\\:_ Folder containing the adjusted *.jpg training files, this include RGB2B&W transformation, brigthness, constrast and noise corrections.
    * _\\text\\:_ Folder containing the training files with the text in *.txt files.
    * _MMC_Train_DataSet.csv:_ CSV file with the pandas dataframe of the training data.
    * _MMC_Alt_Train_DataSet.csv:_ CSV file with the adjusted (word2vec, stopwords, alt-rep, normalization, regularization) pandas dataframe of the training data
    * _Spanish_Stop_Dict.csv:_ CSV file containing the stop word dictionary for spanish.

***
## Important Notes
* _Config.py:_ are Python scripts to work around the relative import of the project local dependencies. It is needed in all script folders such as _lib_, and _Models_.
* All folders in _\\Data\\_ are divided into two distinct subfolders _\\00-Others\\_ and _\\01-Mechas\\_ to recognize the data ownership between **Others** and **MMC**.
* pdf2images.py needs poppler to work, follow the installation instructions in the GitHub URL https://github.com/Belval/pdf2image
***