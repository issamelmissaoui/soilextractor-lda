# coding: utf-8

from flask import Flask, request, render_template, current_app, send_from_directory
from string import punctuation
import re
import os
from werkzeug.utils import secure_filename
from lca_extractor import execute_lca, save_xls
from labomag_extractor import execute_labomag
import pandas as pd

app = Flask(__name__)

UPLOAD_FOLDER = 'static/upload'
DOWNLOAD_FOLDER = 'static/download'
DB_FOLDER = 'static/database'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
app.config['DB_FOLDER'] = DB_FOLDER


with app.app_context() as appli:

    GEN_DOWNLOAD_FOLDER = os.path.join(current_app.root_path, DOWNLOAD_FOLDER)
    UPLOAD_FOLDER = os.path.join(current_app.root_path, UPLOAD_FOLDER)
    DOWNLOAD_FOLDER = os.path.join(current_app.root_path, DOWNLOAD_FOLDER)
    DB_FOLDER = os.path.join(current_app.root_path, DB_FOLDER)



@app.route('/ldase')
def my_form():
    return render_template('form.html')
'''
@app.route('/', methods=['POST'])
def my_form_post():
    
    stop_words = stopwords.words('english')
    
    #convert to lowercase
    text1 = request.form['text1'].lower()
    
    text_final = ''.join(c for c in text1 if not c.isdigit())
    
    #remove punctuations
    #text3 = ''.join(c for c in text2 if c not in punctuation)
        
    #remove stopwords    
    processed_doc1 = ' '.join([word for word in text_final.split() if word not in stop_words])

    sa = SentimentIntensityAnalyzer()
    dd = sa.polarity_scores(text=processed_doc1)
    compound = round((1 + dd['compound'])/2, 2)

    return render_template('form.html', final=compound, text1=text_final,text2=dd['pos'],text5=dd['neg'],text4=compound,text3=dd['neu'])
'''

@app.route('/ldase',methods=['POST'])
def my_form_post():
    
    labo = request.form['labo']
    export_file_name = request.form['exportFile']
    print(labo)
    print(export_file_name)
    '''
    #f = request.files['files']
    #file_name = secure_filename(f.filename)
    #file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
    #f.save(file_path)
    #data_extr = execute([file_path])
    #data_extr['Laboratoire'] = labo.upper()
    #try :
    #    data_extr['Parcelle'] = file_name.split('.')[0].split('P')[1]
    #except : 
    #    data_extr['Parcelle'] = file_name


    #print(file_path)
    '''
    pdf_paths = []
    pdf_names = []
    f = request.files.getlist("files")
    for fle in f:
        fle_name = secure_filename(fle.filename)
        fle_path = os.path.join(app.config['UPLOAD_FOLDER'], fle_name)
        fle.save(fle_path)
        pdf_paths.append(fle_path)
        pdf_names.append(fle_name)

    if labo.lower() == 'lca' :
        data_extr = execute_lca(pdf_paths)
        try :
            data_extr['Parcelle'] = [fname.split('.')[0].split('P')[1].split('_')[0] for fname in pdf_names]
        except : 
            data_extr['Parcelle'] = pdf_names

    elif labo.lower() == 'labomag' or labo.lower() == 'autre': 
        data_extr = execute_labomag(pdf_paths)
        #print(data_extr.iloc[0])


    
    data_extr['Laboratoire'] = labo.upper()

    
    
    prio_columns = ['Domaine','Laboratoire', 'N_Labo','Province','Parcelle','Profondeur','Culture','Date_prélèvement','Date_réception','Date_fin_analyse','Date_édition','pH eau*','Calcaire Total* (%)','Calcaire Actif* (%)','CaO (mg/kg)','A.Phosphorique Olsen (P2O5) (mg/kg)','Potasse K20 (mg/kg)','Magnesie MgO* (mg/kg)','Cuivre (mg/kg)','Zinc (mg/kg)','Fer (mg/kg)','Manganèse (mg/kg)','Bore soluble (mg/kg)','Matière Organique (%)','Ammonium (N-NH4)','Nitrate (N-NO3)','Chlorures (Cl)','EC 1/5 (ms/cm)','Sodium Na2O (mg/kg)']
    other_columns = [col for col in data_extr.columns if col not in prio_columns]
    data_extr_red = data_extr[prio_columns].copy()
    #print(data_extr_red.shape)


    f_db = request.files['fileDb']
    f_db_name = secure_filename(f_db.filename)
    fDb_path = os.path.join(app.config['DB_FOLDER'], f_db_name)
    f_db.save(fDb_path)
    database = pd.read_excel(fDb_path, sheet_name='consolidé')
    print(database.shape)
    database_mod = database.copy()
    if data_extr_red.shape[1] == database_mod.shape[1] : 
        database_mod.columns = prio_columns
        if '0 à 30 cm' in data_extr_red['Profondeur'].values or '0-30 cm' in data_extr_red['Profondeur'].values :
            data_extr_red['Profondeur'] = '0-30'
        elif '0 à 50 cm' in data_extr_red['Profondeur'].values or '0-50 cm' in data_extr_red['Profondeur'].values :
            data_extr_red['Profondeur'] = '0-50'

        data_final = pd.concat([database_mod, data_extr_red]).reset_index(drop=True).copy()
    else : 
        print('no')
        data_final = data_extr.copy()

    columns_f = ['Domaine','Laboratoire', 'N° Labo','Province','Parcelle','Profondeur (cm)','Culture','Date de prélèvement','Date de réception',"Date de fin d'analyse","Date d'édition","pH eau","Calcaire Totale (%)","Calcaire Actif (%)","CaO (mg/kg)","A. Phosphorique P₂O₅ Olsen (mg/kg)", "Potasse K₂O (mg/kg)", "Magnésie MgO (mg/kg)", "Cuivre (mg/kg)", "Zinc (mg/kg)","Fer (mg/kg)","Manganèse (mg/kg)", "Bore (mg/kg)","Matière Organique C* x 1,724", "Ammonium (N-NH₄) (mg/kg)", "Nitrate (N-NO₃) (mg/kg)", "Chlorures (mg/kg)","EC 1/5 (ms/cm)", 'Sodium Na₂O (mg/kg)']
    print(len(columns_f))
    print(len(prio_columns))
    

    data_final.columns = columns_f
    data_final['Parcelle'] = data_final['Parcelle'].apply(lambda x: str(x))
    data_final['Domaine'] = data_final['Domaine'].apply(lambda x: str(x).replace('DOMAINES', 'DOMAINE'))
    print(data_final['Domaine'].unique())
    data_final['Date de prélèvement'] = pd.to_datetime(data_final['Date de prélèvement'], infer_datetime_format=True, errors='ignore') #format="%d/%m/%Y")
    data_final['Date de réception'] = pd.to_datetime(data_final['Date de réception'], infer_datetime_format=True, errors='ignore') #format="%d/%m/%Y")
    data_final["Date de fin d'analyse"] = pd.to_datetime(data_final["Date de fin d'analyse"], infer_datetime_format=True, errors='ignore') #format="%d/%m/%Y")
    data_final["Date d'édition"] = pd.to_datetime(data_final["Date d'édition"], infer_datetime_format=True, errors='ignore') #format="%d/%m/%Y")



    
    data_final_sorted = data_final.sort_values(by=['Domaine', 'Parcelle', 'Date de prélèvement']).copy()

    print(data_final_sorted.tail())
    
    
   

    path_export = os.path.join(app.config['DOWNLOAD_FOLDER'], export_file_name+ '.xlsx')
    save_xls([database, data_final_sorted], path_export)
    '''
    #data_final.to_excel(path_export, index=False)

    # This would save the file. Now to read simply use the normal way to read files in Python

    #with open(file_path, 'r') as f:
    #    file_content = f.read()
    #    print(file_content)
    
    #file_data.save(os.path.join("system","files","text",file_name))
    #with open("system/files/text/file_name") as f:
    #    file_content = f.read()
    #    print(file_content)
    #file = File(f)
    #f.read_file_dif()
    '''
    return render_template('form.html', final=labo, filename=export_file_name)

    #return render_template('form.html', final=labo, text1=file_name)
 
@app.route('/restitution_download/<filename>')
def restitution_download(filename):
    downloads = GEN_DOWNLOAD_FOLDER

    return send_from_directory(directory=downloads, path=filename+'.xlsx')

    #return send_from_directory('database_reports', filename)

if __name__ == "__main__":
    #app.run(debug=True, host="127.0.0.1", port=5002, threaded=True)
    app.run(debug=True, threaded=True)
