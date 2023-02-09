// =======================================================
// 
//          CIC ecrire - Simulation CIC (exemple)
//============================================================    
// Script d'exemple illustrant l'utilisation des fonctions 
// de celestLab en vue de générer les fichiers nécessaires
// pour les sessions d'ingéniérie concourrante (CIC)
// Ce script ne produit pas tous les fichiers nécessaires mais
// uniquement quelques exemples sélectionnées :
//  - fichier position vitesse
//  - fichier quternions d'attitude
//  - Fichier de visibilité géométrique des stations
//  - fichier d'éclipse (visibilité soleil)
//  - fichier direction soleil en repère sat
//  - ficjier direction Terre en repère sat
//  - fichier coordonnées géographiques
//
//              CNES - DCT/SB/MS
//============================================================



function date_str = get_date_str()
  dt=getdate();
  date_str = msprintf("%d",dt(1)) + "-" + msprintf("%02d",dt(2)) + "-" + msprintf("%02d",dt(6)) + "T" + ...
             msprintf("%02d",dt(7)) + ":" + msprintf("%02d",dt(8)) + ":" +  msprintf("%02d",dt(9))+ "." +  msprintf("%03d",dt(10));
endfunction

function entete = entete_MEM(nom_param , prefixe)
  date_str = get_date_str();

  entete = [
  "CIC_MEM_VERS = 1.0"
  "CREATION_DATE  = " + date_str
  "ORIGINATOR     = CNES - DCT/SB/MS"
  ""
  "META_START"
  ""
  "OBJECT_NAME = " + prefixe
  "OBJECT_ID = " + prefixe
  ""
  "USER_DEFINED_PROTOCOL = CIC"
  "USER_DEFINED_CONTENT = " + nom_param
  "TIME_SYSTEM = UTC"
  ""
  "META_STOP"
  ""];
endfunction

function entete = entete_OEM(prefixe)
  date_str = get_date_str();

  entete = [
  "CIC_OEM_VERS = 2.0"
  "CREATION_DATE  = " + date_str
  "ORIGINATOR     = CNES - DCT/SB/MS"
  ""
  "META_START"
  ""
  "OBJECT_NAME = " + prefixe
  "OBJECT_ID = " + prefixe
  ""
  "CENTER_NAME = EARTH"
  "REF_FRAME   = ICRF"
  "TIME_SYSTEM = UTC"
  ""
  "META_STOP"
  ""];
endfunction

function entete = entete_AEM(prefixe, rep_frame_a, rep_frame_b)
  date_str = get_date_str();

  entete = [
  "CIC_AEM_VERS = 1.0"
  "CREATION_DATE  = " + date_str
  "ORIGINATOR     = CNES - DCT/SB/MS"
  ""
  "META_START"
  ""
  "OBJECT_NAME = " + prefixe
  "OBJECT_ID = " + prefixe
  ""
  "REF_FRAME_A = " + rep_frame_a
  "REF_FRAME_B = " + rep_frame_b
  "ATTITUDE_DIR = A2B"
  "TIME_SYSTEM = UTC"
  "ATTITUDE_TYPE = QUATERNION"
  ""
  "META_STOP"
  ""];
endfunction

function write_fic(type_fic, rep ,prefixe, format_date, jour_mjd, sec_mjd, nom_param, val_param, format_param, rep_frame_a, rep_frame_b);
  fd = mopen( rep + filesep() + prefixe + "_" + nom_param + ".TXT" , "wt");
  if (type_fic == "MEM")
    mputl( entete_MEM(nom_param, prefixe),fd);
  elseif (type_fic == "OEM")
    mputl( entete_OEM(prefixe),fd);
  elseif (type_fic == "AEM")
    mputl( entete_AEM(prefixe,rep_frame_a,rep_frame_b),fd);
  else 
    error("Wrong type of type_fic");
  end
  
  // Use mputl and msprintf because mfprintf is really slow (Scilab bug??)
  mputl( msprintf(format_date + format_param + "\n",[jour_mjd ; sec_mjd ;  val_param]'),  fd);
  mclose(fd);
endfunction
