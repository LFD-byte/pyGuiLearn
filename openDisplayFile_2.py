def open_file(filepath):
    with open(filepath, 'r', encoding="utf8") as f:
        data = f.readlines()
    return


def getPatientAndDoctorUtter(content):
    PAD = ''
    for utter in content:
        if utter["speaker"] == "患者":
            PAD = PAD + "P:" + utter["utterance"] + " \n"
        else:
            PAD = PAD + "D:" + utter["utterance"] + " \n"

    return PAD


filepath = "data.00001_00100.json"
data = open_file(filepath)
print(data[0])
PAD = getPatientAndDoctorUtter(eval(data[0])["content"])
print(PAD)