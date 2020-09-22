import re

def compare( report1, report2, error=1e-3 ):
    """
    Compare reports word by word. Float numbers are compared by using a given error.
    """
    words1 = report1.split()
    words2 = report2.split()

    if( len(words1) != len(words2) ):
        return False

    for i in range(len(words1)):
        try:
            float1 = float(words1[i])
            float2 = float(words2[i])

            if( abs(float1-float2) > error ):
                return False
        except ValueError:

            if( words1[i] != words1[i] ):
                return False

    return True
