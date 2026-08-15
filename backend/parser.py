import os

def extract_variants(file_path):
    """
    Reads a VCF file (Supports both 10-column Patient VCFs and 8-column Reference VCFs).
    Translates variants into clinical statuses for the CatBoost ML Model.
    """
    
    # 1. Initialize our target genes to 'Normal' by default.
    patient_data = {
        'CYP2C19': 'Normal',
        'CYP2D6': 'Normal',
        'DPYD': 'Normal',
        'SLCO1B1': 'Normal'
    }
    
    # 2. Our Master Medical Dictionary
    # Expanded to include all rsIDs from the official reference VCFs
    rsid_to_gene_map = {
        # CYP2C19 markers
        'rs12248560': 'CYP2C19', 'rs28399504': 'CYP2C19', 'rs7902257': 'CYP2C19',
        
        # DPYD markers
        'rs3918290': 'DPYD', 'rs1801158': 'DPYD', 
        
        # SLCO1B1 markers
        'rs4149056': 'SLCO1B1', 'rs4149057': 'SLCO1B1',
        
        # CYP2D6 markers (All 22 reference variants added!)
        'rs1065852': 'CYP2D6', 'rs3892097': 'CYP2D6', 'rs12169962': 'CYP2D6',
        'rs1135840': 'CYP2D6', 'rs4987144': 'CYP2D6', 'rs28371730': 'CYP2D6',
        'rs1985842': 'CYP2D6', 'rs16947': 'CYP2D6', 'rs1058164': 'CYP2D6',
        'rs28371702': 'CYP2D6', 'rs28371701': 'CYP2D6', 'rs28371699': 'CYP2D6',
        'rs1081000': 'CYP2D6', 'rs28695233': 'CYP2D6', 'rs29001518': 'CYP2D6',
        'rs1080998': 'CYP2D6', 'rs1080997': 'CYP2D6', 'rs1080996': 'CYP2D6',
        'rs1080995': 'CYP2D6', 'rs28633410': 'CYP2D6', 'rs28624811': 'CYP2D6',
        'rs28735595': 'CYP2D6', 'rs267608321': 'CYP2D6', 'rs1080985': 'CYP2D6'
    }
    
    with open(file_path, 'r') as f:
        for line in f:
            # Skip all header and metadata lines
            if line.startswith('#'): 
                continue
            
            cols = line.strip().split('\t')
            
            # Safety check: Ensure the line has at least the basic 8 columns
            if len(cols) < 8:
                continue
                
            rsid = cols[2]
            info_column = cols[7]
            status = 'Normal'
            
            # ========================================================
            # THE DUAL-MODE LOGIC
            # ========================================================
            if len(cols) >= 10:
                # MODE A: Standard Patient VCF (10+ columns)
                patient_genotype = cols[9].split(':')[0]
                if patient_genotype == '1/1':
                    status = 'Poor'
                elif patient_genotype in ['0/1', '1/0']:
                    status = 'Intermediate'
                    
            elif len(cols) == 8 or len(cols) == 9:
                # MODE B: Official Database VCF (8 columns)
                # Because the file is just a list of mutations, if a row exists here,
                # we assume the patient has the mutated variant. We default to 'Poor'
                # to ensure the AI detects the risk.
                status = 'Poor'
            # ========================================================
            
            # We only do extra processing if a mutation was actually detected
            if status != 'Normal':
                
                # Extract the GENE from the INFO column
                info_dict = {}
                for item in info_column.split(';'):
                    if '=' in item:
                        key_val = item.split('=', 1)
                        if len(key_val) == 2:
                            info_dict[key_val[0]] = key_val[1]
                
                gene = info_dict.get('GENE', 'Unknown')
                
                # Fallback: If 'GENE=' is missing from the file (like in rs1801158.vcf), 
                # look up the rsID in our Master Medical Dictionary.
                if gene == 'Unknown' and rsid in rsid_to_gene_map:
                    gene = rsid_to_gene_map[rsid]

                # 3. Save the worst-case mutation to our final data dictionary
                if gene in patient_data:
                    current_status = patient_data[gene]
                    if status == 'Poor' or (status == 'Intermediate' and current_status == 'Normal'):
                        patient_data[gene] = status
                elif gene != 'Unknown':
                    # If it's a new gene entirely, add it to the dictionary dynamically
                    patient_data[gene] = status
                    
    return patient_data