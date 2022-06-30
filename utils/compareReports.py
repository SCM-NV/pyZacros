import re

def compare( report1, report2, error=None, abs_error=None, rel_error=None ):
    """
    Compare reports word by word. Float numbers are compared by using a given error.
    """
    if error is None and abs_error is None and rel_error is None:
        abs_error = 1e-3
        rel_error = 1e-3
    else:
        if error is not None:
            abs_error = error
            rel_error = error
        if abs_error is not None:
            rel_error = 0.0
        elif rel_error is not None:
            abs_error = 0.0

    lines1 = report1.splitlines()
    lines2 = report2.splitlines()

    if len(lines1) != len(lines2):
        print("Mismatch located in number of lines")
        return False

    for i in range(len(lines1)):
        words1 = lines1[i].split()
        words2 = lines2[i].split()

        if len(words1) != len(words2):
            print("Mismatch located in number of words (line="+str(i+1)+")")
            return False

        for j in range(len(words1)):
            try:
                float1 = float(words1[j])
                float2 = float(words2[j])
                delta = abs(float1-float2)

                thr1 = abs_error + rel_error*abs(float1)
                thr2 = abs_error + rel_error*abs(float2)

                if delta > thr1 or delta > thr2:
                    print("Mismatch located in comparing report (line="+str(i+1)+")")
                    print("> "+str(float1)+" ~ "+str(float2)+"; delta="+str(delta)+", thr1="+str(thr1)+", thr2="+str(thr2))
                    print("Lines:")
                    print("report1> "+lines1[i])
                    print("report2> "+lines2[i])
                    return False
            except ValueError:

                if words1[j] != words2[j]:
                    print("Mismatch located in comparing report (line="+str(i+1)+")")
                    print("> "+words1[j]+" ~ "+words2[j])
                    return False

    return True
