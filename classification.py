
# ======================================== VALIDASI W/ ANOTASI FILE ====================================================

def validasi(read_anotasi,q,s):
    f = open(read_anotasi, 'r')
    lines = f.readlines()
    f.close()

    anotasi_type    = [0]*(len(lines)-2)
    anotasi_sample  = [0]*(len(lines)-2)
    for i in xrange(len(anotasi_type)):
        anotasi_type[i]   = lines[i+2].split(',')[1].strip()
        anotasi_sample[i] = float(lines[i+2].split(',')[0])

    # print anotasi_type
    # print anotasi_sample

    for no_sample in anotasi_sample:
        if( no_sample > q and no_sample < s):
            index_anotasi = anotasi_sample.index(no_sample)
            hasil        = anotasi_type[index_anotasi]
            return hasil #Return 'N' / 'V'


# ======================================= RR ONLY ======================================================================

def by_rr_only(read_anotasi,siklus,mean_rr_i,signal_number):
    TP = 0
    TN = 0
    FP = 0
    FN = 0

    read_v = 0
    read_n = 0
    v_by_algo = 0
    n_by_algo = 0

    for i in range(len(siklus)):
        if(siklus[i][1][0] != 'N/A'):
            rr_i    = siklus[i][5]
            r_i     = siklus[i][2][0]
            q_peak  = siklus[i][1][0]
            s_peak  = siklus[i][3][0]
            q       = signal_number[q_peak] #Membaca nomor sample pada index ke r_i : sample_number (ex. 23453)
            s       = signal_number[s_peak]
            anotasi = validasi(read_anotasi,q,s)

            if(rr_i < 0.9 * mean_rr_i):
                if(anotasi == 'V'):
                    TP += 1
                    read_v += 1
                    v_by_algo += 1
                else:
                    FP += 1
                    read_n += 1
            else:
                if(anotasi == 'N' or anotasi != 'V'):
                    TN += 1
                    read_n += 1
                    n_by_algo += 1
                else:
                    FN += 1
                    read_v += 1
    return TP,TN,FP,FN,read_n,read_v,n_by_algo,v_by_algo

# =========================================== QRS ONLY =================================================================
def by_qrs_morf(read_anotasi,siklus,signal_number):
    TP = 0
    TN = 0
    FP = 0
    FN = 0
    read_v = 0
    read_n = 0
    v_by_algo = 0
    n_by_algo = 0
    for i in range(len(siklus)):
        if(siklus[i][1][0] != 'N/A'):
            rr_type = siklus[i][6]
            q_peak  = siklus[i][1][0]
            s_peak  = siklus[i][3][0]
            q       = signal_number[q_peak] #Membaca nomor sample pada index ke r_i : sample_number (ex. 23453)
            s       = signal_number[s_peak]
            anotasi  = validasi(read_anotasi,q,s)

            if(rr_type == 'negative'):
                if(anotasi == 'V'):
                    TP += 1
                    read_v += 1
                    v_by_algo += 1
                else:
                    FP += 1
                    read_n += 1
            else:
                if(anotasi == 'N' or anotasi != 'V'):
                    TN += 1
                    read_n += 1
                    n_by_algo += 1
                else:
                    FN += 1
                    read_v += 1
    return TP,TN,FP,FN,read_n,read_v,n_by_algo,v_by_algo

# ========================================== RR & QRS ==================================================================
def by_rr_and_qrs_morf(read_anotasi,siklus,mean_rr_i,signal_number):
    TP = 0
    TN = 0
    FP = 0
    FN = 0
    for i in range(len(siklus)):
        if(siklus[i][1][0] != 'N/A'):
            rr_i    = siklus[i][5]
            rr_type = siklus[i][6]
            q_peak  = siklus[i][1][0]
            s_peak  = siklus[i][3][0]
            q       = signal_number[q_peak] #Membaca nomor sample pada index ke r_i : sample_number (ex. 23453)
            s       = signal_number[s_peak]
            anotasi = validasi(read_anotasi,q,s)

            if(rr_type == 'negative'):
                if(rr_i < 0.9 * mean_rr_i):
                    if(anotasi == 'V'):
                        TP += 1
                    else:
                        FP += 1
                else:
                    if(anotasi != 'V'):
                        TN += 1
                    else:
                        FN += 1
            else:
                if(rr_i < 0.9 * mean_rr_i):
                    if(anotasi == 'V'):
                        TP += 1
                    else:
                        FP += 1
                else:
                    if(anotasi != 'V'):
                        TN += 1
                    else:
                        FN += 1
    return TP,TN,FP,FN

# ========================================== RR & P ====================================================================
def by_rr_and_p(read_anotasi,siklus,mean_rr_i,signal_number):
    TP = 0
    TN = 0
    FP = 0
    FN = 0
    for i in range(len(siklus)):
        if(siklus[i][1][0] != 'N/A'):
            rr_i    = siklus[i][5]
            p_peak  = siklus[i][0][0]
            q_peak  = siklus[i][1][0]
            s_peak  = siklus[i][3][0]
            q       = signal_number[q_peak] #Membaca nomor sample pada index ke r_i : sample_number (ex. 23453)
            s       = signal_number[s_peak]
            anotasi = validasi(read_anotasi,q,s)

            if(rr_i < 0.9 * mean_rr_i):
                if(p_peak == 'N/A'):
                    if(anotasi == 'V'):
                        TP += 1
                    else:
                        FP += 1
                else:
                    if(anotasi != 'V'):
                        TN += 1
                    else:
                        FN += 1
            else:
                if(anotasi == 'V'):
                    FN += 1
                else:
                    TP += 1

    return TP,TN,FP,FN

# ======================================= REAL TIME DETECTION ==========================================================

def real_time(siklus,mean_rr_i):
    for i in range(len(siklus)):
        if(siklus[i][1][0] != 'N/A'):
            rr_i    = siklus[i][5]
            r_i     = siklus[i][2][0]

            if(rr_i < 0.9 * mean_rr_i):
                print "siklus ke [",i+1,"] : PVC"
            else:
                print "siklus ke [",i+1,"] : NORMAL"

# ======================================= PEDRO DETECTION ==========================================================

def pedro(siklus,mean_rr,signal_number,read_anotasi):
    TP = 0
    TN = 0
    FP = 0
    FN = 0
    for i in range(len(siklus)-1):
        if(siklus[i][2][0] != 'N/A'):
            rr_i    = siklus[i][5]
            rr_next = siklus[i+1][5]

            prematurity = (float(mean_rr)-float(rr_i))/float(rr_i)
            compensatory = (float(rr_next)-float(mean_rr))/float(mean_rr)

            # print "Prematurity  [",i+1,"] : ", prematurity
            # print "Compensatory [",i+1,"] : ", compensatory

            q_peak  = siklus[i][1][0]
            s_peak  = siklus[i][3][0]
            q       = signal_number[q_peak] #Membaca nomor sample pada index ke r_i : sample_number (ex. 23453)
            s       = signal_number[s_peak]
            anotasi = validasi(read_anotasi,q,s)

            if(prematurity < 0 and compensatory < 0):
                if(anotasi == 'N'):
                    TN += 1
                else:
                    FN += 1
            else:
                if(anotasi == 'V'):
                    TP += 1
                else:
                    FP += 1
    return TP,TN,FP,FN

