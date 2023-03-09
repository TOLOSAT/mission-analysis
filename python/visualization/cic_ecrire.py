# -*- coding: utf-8 -*-
"""
Created on Thu Feb  9 19:40:50 2023

@author: andre
"""

import datetime


def get_date_str():
    dt = datetime.datetime.now()
    date_str = "{}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}.{:03d}".format(dt.year, dt.month, dt.day, dt.hour, dt.minute,
                                                                     dt.second, dt.microsecond // 1000)
    return date_str


def entete_MEM(nom_param, prefixe):
    date_str = get_date_str()

    entete = [
        "CIC_MEM_VERS = 1.0",
        "CREATION_DATE  = " + date_str,
        "ORIGINATOR     = CNES - DCT/SB/MS",
        "",
        "META_START",
        "",
        "OBJECT_NAME = " + prefixe,
        "OBJECT_ID = " + prefixe,
        "",
        "USER_DEFINED_PROTOCOL = CIC",
        "USER_DEFINED_CONTENT = " + nom_param,
        "TIME_SYSTEM = UTC",
        "",
        "META_STOP",
        ""]
    return entete


def entete_OEM(prefixe):
    date_str = get_date_str()

    entete = [
        "CIC_OEM_VERS = 2.0",
        "CREATION_DATE  = " + date_str,
        "ORIGINATOR     = CNES - DCT/SB/MS",
        "",
        "META_START",
        "",
        "OBJECT_NAME = " + prefixe,
        "OBJECT_ID = " + prefixe,
        "",
        "CENTER_NAME = EARTH",
        "REF_FRAME   = ICRF",
        "TIME_SYSTEM = UTC",
        "",
        "META_STOP",
        ""]
    return entete


def entete_AEM(prefixe, rep_frame_a, rep_frame_b):
    date_str = get_date_str()

    entete = [
        "CIC_AEM_VERS = 1.0",
        "CREATION_DATE  = " + date_str,
        "ORIGINATOR     = CNES - DCT/SB/MS",
        "",
        "META_START",
        "",
        "OBJECT_NAME = " + prefixe,
        "OBJECT_ID = " + prefixe,
        "",
        "REF_FRAME_A = " + rep_frame_a,
        "REF_FRAME_B = " + rep_frame_b,
        "ATTITUDE_DIR = A2B",
        "TIME_SYSTEM = UTC",
        "ATTITUDE_TYPE = QUATERNION",
        "",
        "META_STOP",
        ""]
    return entete


'''
 ATTENTION HERE: this assumes we have all the needed parameters for the function:
 type_fic will be MEM; OEM or AEM
 (!!!!!!) If the file is at C:\\Users\\andre\\Desktop\\TOLOSAT\\test.TXT, this needs to have:
        rep =  "C:\\Users\\andre\\Desktop\\TOLOSAT"
        prefixe = "test"
 DON'T FORGET TO DECLARE THE PATHS WITH TWO BACKSLASHES (\\), AS PYTHON ONLY RECOGNIZES IT LIKE THIS!
'''
def write_fic(type_fic, rep, prefixe, format_date, jour_mjd, sec_mjd, nom_param, val_param, format_param, rep_frame_a,
              rep_frame_b):
    PATH = str(rep) + "\\" + str(prefixe) + ".TXT"
    fd = open(PATH, "w")
    if (type_fic == "MEM"):
        fd.write(str(entete_MEM(nom_param, prefixe)))
    elif (type_fic == "OEM"):
        fd.write(str(entete_OEM(prefixe)))
    elif (type_fic == "AEM"):
        fd.write(str(entete_AEM(prefixe, rep_frame_a, rep_frame_b)))
    else:
        print("Wrong type of type_fic")

    outputList = [jour_mjd, sec_mjd, val_param]

    fd.write((str(format_date) + str(format_param) + "\n" + str(outputList))
    fd.close()
    return
