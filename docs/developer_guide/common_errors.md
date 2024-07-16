# SVD developer guide - Common issues

## ISSUE CODE #1 - Wrong panel applied

The following information should be supplied along with the request:
- *SampleAnalysis PK* - the primary key of the SampleAnalysis object that needs to be removed (unless requested otherwise)
- *Sample ID*
- *Current panel (the incorrect one)*
- *Correct panel (the one to be applied)*
- *Worksheet ID*
- *Run ID*

Instructions
- Open the LP-GEN-TSO500Bioinf SOP
- Navigate to section 3.7 - FAQs
- To add the correct panel, follow the process in part 8 - Uploading a sample with a new referral
- To remove the incorrect panel (if required), follow part 2 - Removing a sample analysis from the somatic variant database

## ISSUE CODE #2 - Variant needs to be removed from the poly list

The following information should be supplied along with the request:
- *VariantToVariantList PK* - the primary key of the VaraintToVariantList object that needs to be removed
- *Variant* - the genomic co-ordinates of the variant to be removed, to be used as a sanity check

Instructions
- Make sure all of the info above has been supplied, if not then ask the clinical scientist to provide it
- Log in as admin and go to the database admin page
- Click of the 'Variants to variant lists' link
- Click on the link for the object that matches the PK given above (i.e. if the PK is 1, click on 1)
- Sanity check that the linked Variant object matches the information that was provided above
- If the information matches, click Delete
- On the next page, make sure that only one VariantToVariantList object is going to be removed and if so, click 'Yes, I'm sure'
- If you're not sure then ask for help from another member of the team
