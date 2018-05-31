import matplotlib.pyplot as plt
import filtering as filt
import classification as detect
import bwr

def mean(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)

def main_test(lines,fig,data_title,signal_type,read_anotasi):
# def main_test(lines,fig,data_title,signal_type):
    raw_signal      = [0]*(len(lines)-2)
    signal_number   = [0]*(len(lines)-2)
    for i in xrange(len(raw_signal)):
        raw_signal[i]    = float(lines[i+2].split(',')[signal_type])
        signal_number[i] = float(lines[i+2].split(',')[0])
    len_sample = len(raw_signal)

    plt.figure(fig)
    plt.subplot(211); plt.tight_layout()
    plt.title('Raw signal '+data_title)
    plt.plot(range(len(raw_signal)),raw_signal)


    #___________________________________________2.1 ECG FILTERING_______________________________________________________

    (baseline, raw_signal) = bwr.bwr(raw_signal)
    ecg_der = filt.five_point_derivative(raw_signal) #(MARHOON)
    ecg_adp = filt.adaptive_filter(ecg_der) #(MARHOON)

    #___________________________________________2.1 FEATURE EXTRACTION__________________________________________________
    sampled_window = len_sample
    sample = []
    for i in range(sampled_window):
        sample.append(ecg_adp[i-1])

    plt.subplot(212); plt.tight_layout()
    plt.plot(range(len(sample)),sample)
    plt.title('Hasil Ciri '+data_title)

    # 1. Get Maximum Value From Data
    MAX = max(sample)

    # 2. OBTAIN R-PEAK USING THRESHOLD t = (0.4) * MAX (UMER w/ verification R Peak)
    R            = 0.4 * MAX
    list_upper   = []
    r_peaks      = []
    r_intervals  = []
    r_values     = []
    for i in range(sampled_window - 1):
        if(sample[i] > R):
            if(len(list_upper) == 0):
                list_upper.append(sample[i])
            else:
                list_upper.append(sample[i])
                if(sample[i+1] < R):
                    r_peak = max(list_upper)
                    r_in = sample.index(r_peak)
                    r_peaks.append([r_in, r_peak])
                    list_upper = []

    # 3. CREATE RR-INTERVAL LIST & INITIATE SIKLUS
    siklus = []
    for i in range(len(r_peaks) - 1):
        r1      = r_peaks[i][0]
        r2      = r_peaks[i + 1][0]
        rr      = r2 - r1

        r   = r_peaks[i+1]
        p   = ['N/A','N/A']
        q   = ['N/A','N/A']
        s   = ['N/A','N/A']
        t   = ['N/A','N/A']
        r_type = 'positive'
        siklus.append([p,q,r,s,t,rr,r_type])
        r_intervals.append(rr)


    # 4. FIND UNDETECTED R-PEAK
    new_siklus = []
    first_r    = r_peaks[0][0]
    last_r     = r_peaks[-1][0]
    # print "first R : ", first_r, last_r
    for i in range(len(siklus)):
        rr_i    = siklus[i][5]
        r_i     = siklus[i][2][0]
        r_start = r_i - rr_i
        r_prev  = r_start
        if(rr_i > 1.8 * mean(r_intervals)):
            decrease_th     = 0.3 * MAX
            s_onset         = r_start + ((15 * rr_i)/100)
            p_offset        = r_i - ((35 * rr_i)/100)
            list_new_upper  = []
            temp_siklus_new = []
            temp_index = []
            temp_k = 0
            for j in sample[s_onset:p_offset]:
                if(j > decrease_th):
                    if(len(list_new_upper) == 0):
                        list_new_upper.append(j)
                    else:
                        list_new_upper.append(j)
                        a = sample.index(j)
                        b = sample[a+1]
                        if(b < decrease_th):
                            r_peak_new      = max(list_new_upper)
                            r_i_new         = sample.index(r_peak_new)
                            temp_index.append(r_i_new)
                            # r_peaks.append([r_i_new,r_peak_new])
                            rr_i_new        = r_i_new - r_prev
                            siklus_new      = [ ['N/A','N/A'],['N/A','N/A'],[r_i_new,r_peak_new],['N/A','N/A'],['N/A','N/A'],rr_i_new,'positive' ]
                            list_new_upper  = []
                            r_prev          = r_i_new
                            temp_siklus_new.append(siklus_new)
                            new_siklus.append(siklus_new)
            new_siklus.append(siklus[i])
        else:
            new_siklus.append(siklus[i])
    siklus = new_siklus

    # 6. REMOVE FALSE R-PEAK
    # siklus = find_false_peak(sample,new_siklus,mean(r_intervals),r_peaks)

    # 7. UPDATE INTERVALS
    for i in range(len(siklus)):
        r_i = siklus[i][2][0]
        if(i == 0 and r_i != first_r):
            siklus[i][5] = r_i - first_r
        else:
            siklus[i][5] = r_i - siklus[i-1][2][0]


    # 8. DETECT POSITION OF R_PEAK (-)/(+) SHOULD BE, AND APPEND TO R_PEAKS
    new_r_intervals = []
    for i in range(len(siklus)):
        rr_i            = siklus[i][5]
        r_i             = siklus[i][2][0]

        if(i < len(siklus) - 1):
            rr_next     = siklus[i+1][5]
        else:
            rr_next     = rr_i

        if(i == 0):
            r_prev      = first_r
        else:
            r_prev      = r_i - rr_i


        min_val         = min(sample[r_prev:r_i])
        min_index       = sample.index(min_val)
        s_offset        = r_prev + ((15 * rr_i)/100)
        s_offset_i      = r_i + ((15 * rr_next)/100)
        if( r_prev < s_offset):
            s_val_r_prev    = min(sample[r_prev:s_offset])
        else:
            s_val_r_prev    = min(sample[r_prev:r_prev + 100])
        # print r_i, s_offset_i, r_i < s_offset_i
        if( r_i < s_offset_i):
            s_val_r_i       = min(sample[r_i:s_offset_i])
        else:
            s_val_r_i       = min(sample[r_i:r_i + 100])
        q_onset         = r_i - ((5 * rr_i)/100)

        half_interval   = r_prev + ((50 * rr_i)/100)

        # (-) BEAT
        if( min_index > half_interval and min_val < 1.1 * s_val_r_prev and min_val < 1.5 * s_val_r_i ):
            # plt.plot(min_index, min_val, 'b.', markersize=10) #Plot the MIN peak

            # Update Current RR Interval
            rr_i            = min_index - r_prev
            siklus[i][5]    = rr_i
            # Update Next RR Interval
            if(i < len(siklus) - 1):
                r_next         = siklus[i+1][2][0]
                rr_next        = r_next - min_index
                siklus[i+1][5] = rr_next
            # Change R Position
            siklus[i][2][0] = min_index
            siklus[i][2][1] = min_val
            siklus[i][6]    = "negative"

        new_r_intervals.append(rr_i)
        r_values.append(siklus[i][2][1])


    # 9. PLOT P,Q,S,T PEAK USING RR
    t_threshold = 0.1 * mean(r_values)
    plt.axhline(y=t_threshold, color='#42f486')
    for i in range(len(siklus)-1):
        r_i  	= siklus[i][2][0]
        r_v  	= siklus[i][2][1]
        rr_i 	= siklus[i][5]

        r_prev	= r_i - rr_i
        r_type  = siklus[i][6]

        r_i_next  	= siklus[i+1][2][0]
        r_v_next  	= siklus[i+1][2][1]
        if(i == len(siklus) - 1):
            rr_i_next 	= siklus[i][5]
        else:
            rr_i_next 	= siklus[i+1][5]
        r_prev_next	= r_i_next - rr_i
        r_type_next = siklus[i+1][6]

        # ============ DETECT Q & S =============

        q_on            = r_i - ((10 * rr_i_next)/100)
        if(q_on != r_i):
            if(r_type == "positive"):
                q_peak      = min(sample[q_on:r_i])
            else:
                q_peak      = max(sample[q_on:r_i])

            q_in            = sample.index(q_peak)
            siklus[i][1][0] = q_in
            siklus[i][1][1] = q_peak

        s_on            = r_i + ((15 * rr_i_next)/100)
        if(s_on != r_i):
            if(r_type == "positive"):
                s_peak      = min(sample[r_i:s_on])
            else:
                s_peak      = max(sample[r_i:s_on])
            s_in            = sample.index(s_peak)
            siklus[i][3][0] = s_in
            siklus[i][3][1] = s_peak

        # ============ DETECT P & T =============

        # t_on    = r_i + ((15 * rr_i_next)/100)
        # t_off   = r_i + ((55 * rr_i_next)/100)
        # double_rr = rr_i + rr_i_next
        # if(rr_i < 0.4 * double_rr):
        #     p_on    = r_i - ((70 * rr_i)/100)
        # else:
        #     p_on    = r_i - ((35 * rr_i)/100)
        #
        # p_off   = r_i - ((10 * rr_i)/100)
        #
        # t_peak  = max(sample[t_on:t_off])
        # t_in    = sample.index(t_peak)
        # p_peak  = max(sample[p_on:p_off])
        # p_in    = sample.index(p_peak)
        #
        # siklus[i][4][0] = t_in
        # siklus[i][4][1] = t_peak
        #
        # t_on_prev    = r_prev + ((15 * rr_i)/100)
        # t_off_prev   = r_prev + ((80 * rr_i)/100)
        # t_peak_prev  = max(sample[t_on_prev:t_off_prev])
        # t_in_prev    = sample.index(t_peak)
        #
        # if(p_in == t_in_prev):
        #     siklus[i][0][0] = 'N/A'
        #     siklus[i][0][1] = 'N/A'
        # else:
        #     siklus[i][0][0] = p_in
        #     siklus[i][0][1] = p_peak


    # 9. PLOT ALL PEAK USING SIKLUS
    for i in range(len(siklus)):
        # print siklus[i]
        # r_values.append(siklus[i][2][1])
        new_r_intervals.append(siklus[i][5])
        if(siklus[i][1][0] != 'N/A' and siklus[i][2][0] != 'N/A' and siklus[i][3][0] != 'N/A'):
            # plt.plot(siklus[i][0][0], siklus[i][0][1], 'm.', markersize=10) #Plot the P peak
            plt.plot(siklus[i][1][0], siklus[i][1][1], 'y.', markersize=10) #Plot the Q peak
            plt.plot(siklus[i][2][0], siklus[i][2][1], 'r.', markersize=10) #Plot the R peak
            plt.plot(siklus[i][3][0], siklus[i][3][1], 'g.', markersize=10) #Plot the S peak
            # plt.plot(siklus[i][4][0], siklus[i][4][1], 'c.', markersize=10) #Plot the T peak

    print "-------------------------------------"
    print "Mean R-Value    = ", mean(r_values)
    print "Mean R-Interval = ", mean(new_r_intervals)
    print "Length Siklus   = ", len(siklus)
    # print "Total R peaks : ", len(r_peaks)
    # print "Total S peaks : ", len(s_peaks)
    # print "Total Q peaks : ", len(q_peaks)
    # print "Total P peaks : ", len(p_peaks)
    # print "Total T peaks : ", len(t_peaks)


    #___________________________________________2.2 CLASSIFICATION______________________________________________________
    if( signal_type != 0 ):
        TP,TN,FP,FN,N,V,Na,Va = detect.by_rr_only(read_anotasi,siklus,mean(new_r_intervals),signal_number)
        print  TP,TN,FP,FN," | Read N : ", N, " | Read V : ", V," | Na : ",Na," | Va : ", Va
        print "By RR             : acc(", accuracy(TP,TN,FP,FN),"%) | spc (", specificity(TN,FP),"%) | sns(", sensitivity(TP,FN),"%)"

        TP,TN,FP,FN,N,V,Na,Va = detect.by_qrs_morf(read_anotasi,siklus,signal_number)
        print  TP,TN,FP,FN," | Read N : ", N, " | Read V : ", V," | Na : ",Na," | Va : ", Va
        print "By QRS Morphology : acc(", accuracy(TP,TN,FP,FN),"%) | spc (", specificity(TN,FP),"%) | sns(", sensitivity(TP,FN),"%)"

        # TP,TN,FP,FN = detect.by_rr_and_qrs_morf(read_anotasi,siklus,mean(new_r_intervals),signal_number)
        # print "By QRS & RR       : ", TP,TN,FP,FN, "|",accuracy(TP,TN,FP,FN),'%'
        #
        # TP,TN,FP,FN = detect.by_rr_and_p(read_anotasi,siklus,mean(new_r_intervals),signal_number)
        # print "By QRS & P        : ", TP,TN,FP,FN, "|",accuracy(TP,TN,FP,FN),'%'

        # TP,TN,FP,FN = detect.pedro(siklus,mean(new_r_intervals),signal_number,read_anotasi)
        # print "By PEDRO : acc(", accuracy(TP,TN,FP,FN),"%) | spc (", specificity(TN,FP),"%) | sns(", sensitivity(TP,FN),"%)"
    else:
        detect.real_time(siklus,mean(new_r_intervals))

    print "-------------------------------------"
    #___________________________________________________________________________________________________________________

def find_false_peak(sample,siklus,mean_r_intervals,r_peaks):
    first_r      = r_peaks[0][0]
    idx   = []
    for i in range(len(siklus)-1):
        rr_i        = siklus[i][5]
        r_v         = siklus[i][2][1]

        if(i == 0):
            r_prev  = first_r
        else:
            r_prev  = siklus[i-1][2][0]

        r_prev_v   = sample[r_prev]

        double_rr  = rr_i + siklus[i+1][5]

        if(rr_i < 0.2 * double_rr):
            if(r_v > r_prev_v):
                idx.append(i-1)
            else:
                idx.append(i)

    j = len(idx) - 1
    while j >= 0:
        siklus.pop(idx[j])
        j = j - 1

    return siklus

def accuracy(tp,tn,fp,fn):
    a = tp + tn
    b = tp + tn + fp + fn
    try:
        return float(a)/float(b) * 100
    except ZeroDivisionError:
        return 0

def specificity(tn,fp):
    a = tn
    b = tn + fp
    try:
        return float(a)/float(b) * 100
    except ZeroDivisionError:
        return 0

def sensitivity(tp,fn):
    a = tp
    b = tp + fn
    try:
        return float(a)/float(b) * 100
    except ZeroDivisionError:
        return 0

