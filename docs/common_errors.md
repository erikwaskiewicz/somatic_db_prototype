# Common issues

### ISSUE CODE #1 - Wrong panel applied

TODO - add from SOP

### ISSUE CODE #2 - Variant needs to be removed from the poly list

The following information should be supplied along with the request:
- *VariantToVariantList PK* - the primary key of the VaraintToVariantList object that needs to be removed
- *Variant* - the genomic co-ordinates of the variant to be removed, to be used an a sanity check

Instructions
- Make sure all of the info above has been supplied, if not then ask the clinical scientist to provide it
- Log in as admin and go to the database admin page
- Click of the 'Variants to variant lists' link
- Click on the link for the object that matches the PK given above (i.e. if the PK is 1, click on 1)
- Sanity check that the linked Variant object matches the information that was provided above
- If the information matches, click Delete
- On the next page, make sure that only one VariantToVariantList object is going to be removed and if so, click 'Yes, I'm sure'
- If you're not sure then ask for help from another member of the team
