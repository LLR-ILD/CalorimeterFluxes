def create_histogram_function(histograms_to_select, system, function):
    function_name = "process_hits_{}_{}".format(system, function)
    function_body = """
def {}(hist_time, hist_time_high, hist_time_hit, upper_hist_time_hit, hist_lower_scale,
    hist_upper_scale, hist_energy, scaled_hist_upper_scale, scaled_hist_energy, function_selection, index, Nhit,
    threshold, low_energy_threshold, low_time_threshold, hit_duration_low_threshold, time_start,
    energy, MIP_scaled_energy, subhit_information):
    """.format(function_name)
        
    if histograms_to_select["low_#Nhits"] or histograms_to_select["high_#Nhits"] or histograms_to_select["all_#Nhits"]:
        function_body += """
    if energy > threshold:
        Nhit[index] += 1
    """
        
    if histograms_to_select["lower_scale_energy"] and histograms_to_select["upper_scale_energy"]:
        function_body += """
    if energy < low_energy_threshold:
        hist_lower_scale.Fill(energy)
    else:
        hist_upper_scale.Fill(energy)
    """
        if histograms_to_select["scaled_upper_scale_energy"]:
            function_body += """
        scaled_hist_upper_scale.Fill(MIP_scaled_energy)
        """    
    elif histograms_to_select["lower_scale_energy"]:
        function_body += """
    if energy < low_energy_threshold:
        hist_lower_scale.Fill(energy)
    """
        if histograms_to_select["scaled_upper_scale_energy"]:
            function_body += """
    else:
        scaled_hist_upper_scale.Fill(MIP_scaled_energy)
    """    
    elif histograms_to_select["upper_scale_energy"]:
        function_body += """
    if energy > low_energy_threshold:
        hist_upper_scale.Fill(energy)
    """
        if histograms_to_select["scaled_upper_scale_energy"]:
            function_body += """
        scaled_hist_upper_scale.Fill(MIP_scaled_energy)
        """       
    
    if histograms_to_select["all_scale_energy"]:
        function_body += """
    hist_energy.Fill(energy)
    """
                                  
    if histograms_to_select["scaled_all_scale_energy"]:
        function_body += """
    scaled_hist_energy.Fill(MIP_scaled_energy)
    """

    time_flag = True
    
    if histograms_to_select["hit_time"] or histograms_to_select["hit_time_high"]:
        time_flag = False
        function_body += """
    subhit_max = -float("inf")
    subhit_min = float("inf")
    for subhit in subhit_information:
        if subhit.time > subhit_max : subhit_max = subhit.time
        if subhit.time < subhit_min : subhit_min = subhit.time
    """
    
    
    if time_flag and (histograms_to_select["time"] or histograms_to_select["time_high"]):
        function_body += """
    for subhit in subhit_information:
    """
            
    
    
    if histograms_to_select["time"] and histograms_to_select["time_high"]:
        function_body += """
        if subhit.time <= low_time_threshold:
            hist_time.Fill(subhit.time, subhit.energy)
        else:
            hist_time_high.Fill(subhit.time, subhit.energy)
        """  
    elif histograms_to_select["time"]:
        function_body += """
        if subhit.time <= low_time_threshold:
            hist_time.Fill(subhit.time, subhit.energy)
        """
    elif histograms_to_select["time_high"]:
        function_body += """
        if subhit.time > low_time_threshold:
            hist_time_high.Fill(subhit.time, subhit.energy)
        """  
    
    
    
    if histograms_to_select["hit_time"] and histograms_to_select["hit_time_high"]:
        function_body += """
    hit_duration = subhit_max-subhit_min
    if hit_duration < hit_duration_low_threshold:
        hist_time_hit.Fill(hit_duration, subhit_min)
    elif hit_duration > hit_duration_low_threshold and subhit_min > time_start:
        upper_hist_time_hit.Fill(hit_duration, subhit_min)    
    """
    elif histograms_to_select["hit_time"]:
        function_body += """
    hit_duration = subhit_max-subhit_min
    if hit_duration < hit_duration_low_threshold:
        hist_time_hit.Fill(hit_duration, subhit_min)
    """
    elif histograms_to_select["hit_time_high"]:    
        function_body += """
    hit_duration = subhit_max-subhit_min
    if hit_duration > hit_duration_low_threshold and subhit_min > time_start:
        upper_hist_time_hit.Fill(hit_duration, subhit_min)  
    """
    return function_body

dic = {"time":True, "time_high":True, "hit_time":True, "hit_time_high":True, "lower_scale_energy":True, "upper_scale_energy": True, "all_scale_energy":True, "scaled_upper_scale_energy": True, "scaled_all_scale_energy":True, "low_#Nhits": True, "high_#Nhits": True, "all_#Nhits": True}

print(create_histogram_function(dic, "lol", "sad"))
