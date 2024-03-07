import gzip

### Read in VCF and convert to dictionary

def read_in_vcf(vcf_path):
    """
    Read in vcf
    """

    with gzip.open(vcf_path, "rt") as f:
        vcf_contents = f.readlines()
    
    header_lines = [line for line in vcf_contents if line.startswith("#")]
    variants = [line for line in vcf_contents if not line.startswith("#")]

    return header_lines, variants


def get_variant_keys(description_line):
    """
    get the vcf fields from the description line of the header
    """ 

    #remove the # and whitespace
    description_line = description_line[1:].rstrip()

    # split on tab
    variant_keys = description_line.split("\t")

    # make lower case
    variant_keys = [key.lower() for key in variant_keys]

    return variant_keys


def get_vep_fields_from_header(header_lines):
    """
    Get the vep info fields from the VCF header
    """

    for line in header_lines:

        # select the VEP line
        if line.startswith("##INFO=<ID=CSQ"):

            # get the VEP fields from the header
            vep_info_line = line.split("Format: ")[1].split('">')[0]

            # split on |
            vep_info_fields = vep_info_line.split("|")

            # make lower case
            vep_info_fields = [field.lower() for field in vep_info_fields]
    return vep_info_fields


def convert_info_field_to_dict(info_field, vep_info_fields):
    """
    Converts the variant 'info' field in to a dictionary
    """
    info_dict = {}
    info_field = info_field.split(";")

    for field in info_field:
        split_field = field.split("=")
        try:
            info_dict[split_field[0]] = split_field[1]
        except IndexError:
            # 'genic' doesn't have a key
            info_dict[split_field[0]] = split_field[0]

    # convert VEP annotation (CSQ) to dict
    vep_annotation_dict = {}
    vep_annotation = info_dict["CSQ"].split(",")
    for transcript_info in vep_annotation:
        values = transcript_info.split("|")
        transcript_dict = dict(zip(vep_info_fields, values))
        transcript = transcript_dict['hgvsc']
        vep_annotation_dict[transcript] = transcript_dict
    
    # update info dict
    info_dict["csq"] = vep_annotation_dict
    del info_dict["CSQ"]

    return info_dict


def convert_sample_information_to_dict(format_and_sample_info, format_and_sample_keys):
    """
    For each sample, create a format dictionary with sample values
    """
    samples_info_dict = {}
    # create a list of keys from the format field
    format_keys = format_and_sample_info["format"].split(":")
    # make format keys lower case
    format_keys = [key.lower() for key in format_keys]
    # get the list of samples
    sample_keys = format_and_sample_keys[1:]
    # for each sample, create a dictionary of the format information
    for key in sample_keys:
        sample_values = format_and_sample_info[key].split(":")
        sample_info_dict = dict(zip(format_keys, sample_values))
        samples_info_dict[key] = sample_info_dict
    return samples_info_dict


def create_variants_dictionary(variant_keys, variants, vep_info_fields):
    """
    create a dictionary containing all the variant information
    """

    # create empty dictionary
    variants_dictionary = {}

    # loop through variants
    for variant in variants:
        
        # strip whitespace
        variant = variant.rstrip()

        # split by tab 
        variant = variant.split("\t")

        # create info dictionary
        variant_dict = dict(zip(variant_keys, variant))

        # convert the info field to a dictionary
        variant_info_field = variant_dict["info"]
        variant_info_dict = convert_info_field_to_dict(variant_info_field, vep_info_fields)
        variant_dict["info"] = variant_info_dict

        # convert the format information for each sample into a dictionary
        format_and_sample_keys = variant_keys[8:]
        format_and_sample_info = {}
        for key in format_and_sample_keys:
            format_and_sample_info[key] = variant_dict[key]
        samples_info_dict = convert_sample_information_to_dict(format_and_sample_info, format_and_sample_keys)
        # update main dictionary, remove format key, value as no longer needed
        variant_dict.update(samples_info_dict)
        del variant_dict["format"]

        # get unique variant name
        variant_name = f"{variant_dict['chrom']}:{variant_dict['pos']}:{variant_dict['ref']}:{variant_dict['alt']}"

        # append variant info to variants dictionary
        variants_dictionary[variant_name] = variant_dict

    return variants_dictionary


def vcf_to_variants_dictionary(vcf_path):
    vcf_header_lines, vcf_variants = read_in_vcf(vcf_path)
    variant_keys = get_variant_keys(vcf_header_lines[-1])
    vep_info_fields = get_vep_fields_from_header(vcf_header_lines)
    variants_dictionary = create_variants_dictionary(variant_keys, vcf_variants, vep_info_fields)
    return variants_dictionary
