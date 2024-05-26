import re,os
from .log import msg
from .functions import bcolors

PATH:str = os.getcwd() or "/"

def CreateWordlist(name:str,worktime:str,data:list) -> None:
    try:
        if data:
            with open(name + "_" + worktime + ".txt","a+") as File:
                for i in data:
                    if i:
                        File.write(i + "\n")
                    else:
                        pass
            msg(f"{bcolors.WARNING}Wordlist Generated. -> {bcolors.ENDC}" + name + "_" + worktime + ".txt")
            File.close()
        else:
            pass
    except Exception as Error:
        msg(f"An Error Occurred: {Error}")


def SaveData(data:str,name:str,worktime:str) -> None:
    try: 
        with open(worktime + "_" + name + "_data.log","a+") as File:
            for item in data:
                if item:
                    if isinstance(item, str):
                        File.write(item + "\n")
                    if isinstance(item, tuple):
                        for element in item:
                            if element:
                                File.write(element + "\n")
                            else:
                                pass
                    else:
                        pass
                else:
                    pass
        File.close()
    except Exception as Error:
        msg(f"An Error Occurred: {Error}")

def RemoveData(worktime:str,name:str) -> None:
    Path = PATH + "/"+ worktime + "_" + name + "_data.log"
    if os.path.isfile(Path):
        os.remove(Path)
    else:
        pass

def ReadData(worktime:str,name:str) -> dict:
    try: 
        with open(worktime + "_" + name + "_data.log","r") as File:
            Data = [domain.strip() for domain in File.readlines()]
            RemoveData(worktime,name)
            try:
                UniqData = list(set(Data))
                CreateWordlist(name,worktime,UniqData)
                return UniqData
            except KeyboardInterrupt:
                pass
    except Exception as Error:
        msg(f"An Error Occurred: {Error}")



def GetPossibleSensitiveInformation(source_code:str,worktime:str) -> None:
    pattern:str = (
                r"(\b\d{6,15}\b)|(\b(?:\d{3}[-.\s]?){2}\d{4}\b)"
                r"|"
                r"(\b(?:password|pwd|pass|secret|token|auth|credentials|username)\b)"
                r"|"
                r"(\b(?:admin|root|test|guest|user|letmein|welcome|administrator|login|bluemoon)\b)"
                r"|"
                r"(\b(?:qwerty|love|cool|hello|world|abc123|123abc|love123|cool123|hello123|mysql|3rjs1la7qe)\b)"
                r"|"
                r"(\b(?:oracle|ftp|puppet|ansible|ec2-user|vagrant|azureuser|aa12345678|qwertyuiop|password123|1q2w3e)\b)"
                r"|"
                r"(\b(?:123qwe|password1|dragon|princess|lovely|aa123456|charlie|qazwsx|sunshine|master|zxcvbnm|18atcskd2w)\b)"
            )

    result = re.findall(pattern, source_code)
    emails_username = [i.split("@")[0] for i in re.findall(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b", source_code)]
    #return result + emails_username
    SaveData(result + emails_username,"GetPossibleSensitiveInformation",worktime)


def GetEmails(source_code:str,worktime:str) -> None:
    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
    emails = re.findall(pattern, source_code)
    #return emails
    SaveData(emails,"GetEmails",worktime)

