const semTypesAbrvToFull = {
    "aapp": "Amino Acid, Peptide, or Protein",
    "acab": "Acquired Abnormality",
    "acty": "Activity",
    "aggp": "Age Group",
    "amas": "Amino Acid Sequence",
    "amph": "Amphibian",
    "anab": "Anatomical Abnormality",
    "anim": "Animal",
    "anst": "Anatomical Structure",
    "antb": "Antibiotic",
    "arch": "Archaeon",
    "bacs": "Biologically Active Substance",
    "bact": "Bacterium",
    "bdsu": "Body Substance",
    "bdsy": "Body System",
    "bhvr": "Behavior",
    "biof": "Biologic Function",
    "bird": "Bird",
    "blor": "Body Location or Region",
    "bmod": "Biomedical Occupation or Discipline",
    "bodm": "Biomedical or Dental Material",
    "bpoc": "Body Part, Organ, or Organ Component",
    "bsoj": "Body Space or Junction",
    "celc": "Cell Component",
    "celf": "Cell Function",
    "cell": "Cell",
    "cgab": "Congenital Abnormality",
    "chem": "Chemical",
    "chvf": "Chemical Viewed Functionally",
    "chvs": "Chemical Viewed Structurally",
    "clas": "Classification",
    "clna": "Clinical Attribute",
    "clnd": "Clinical Drug",
    "cnce": "Conceptual Entity",
    "comd": "Cell or Molecular Dysfunction",
    "crbs": "Carbohydrate Sequence",
    "diap": "Diagnostic Procedure",
    "dora": "Daily or Recreational Activity",
    "drdd": "Drug Delivery Device",
    "dsyn": "Disease or Syndrome",
    "edac": "Educational Activity",
    "eehu": "Environmental Effect of Humans",
    "elii": "Element, Ion, or Isotope",
    "emod": "Experimental Model of Disease",
    "emst": "Embryonic Structure",
    "enty": "Entity",
    "enzy": "Enzyme",
    "euka": "Eukaryote",
    "evnt": "Event",
    "famg": "Family Group",
    "ffas": "Fully Formed Anatomical Structure",
    "fish": "Fish",
    "fndg": "Finding",
    "fngs": "Fungus",
    "food": "Food",
    "ftcn": "Functional Concept",
    "genf": "Genetic Function",
    "geoa": "Geographic Area",
    "gngm": "Gene or Genome",
    "gora": "Governmental or Regulatory Activity",
    "grpa": "Group Attribute",
    "grup": "Group",
    "hcpp": "Human-caused Phenomenon or Process",
    "hcro": "Health Care Related Organization",
    "hlca": "Health Care Activity",
    "hops": "Hazardous or Poisonous Substance",
    "horm": "Hormone",
    "humn": "Human",
    "idcn": "Idea or Concept",
    "imft": "Immunologic Factor",
    "inbe": "Individual Behavior",
    "inch": "Inorganic Chemical",
    "inpo": "Injury or Poisoning",
    "inpr": "Intellectual Product",
    "irda": "Indicator, Reagent, or Diagnostic Aid",
    "lang": "Language",
    "lbpr": "Laboratory Procedure",
    "lbtr": "Laboratory or Test Result",
    "mamm": "Mammal",
    "mbrt": "Molecular Biology Research Technique",
    "mcha": "Machine Activity",
    "medd": "Medical Device",
    "menp": "Mental Process",
    "mnob": "Manufactured Object",
    "mobd": "Mental or Behavioral Dysfunction",
    "moft": "Molecular Function",
    "mosq": "Molecular Sequence",
    "neop": "Neoplastic Process",
    "nnon": "Nucleic Acid, Nucleoside, or Nucleotide",
    "npop": "Natural Phenomenon or Process",
    "nusq": "Nucleotide Sequence",
    "ocac": "Occupational Activity",
    "ocdi": "Occupation or Discipline",
    "orch": "Organic Chemical",
    "orga": "Organism Attribute",
    "orgf": "Organism Function",
    "orgm": "Organism",
    "orgt": "Organization",
    "ortf": "Organ or Tissue Function",
    "patf": "Pathologic Function",
    "phob": "Physical Object",
    "phpr": "Phenomenon or Process",
    "phsf": "Physiologic Function",
    "phsu": "Pharmacologic Substance",
    "plnt": "Plant",
    "podg": "Patient or Disabled Group",
    "popg": "Population Group",
    "prog": "Professional or Occupational Group",
    "pros": "Professional Society",
    "qlco": "Qualitative Concept",
    "qnco": "Quantitative Concept",
    "rcpt": "Receptor",
    "rept": "Reptile",
    "resa": "Research Activity",
    "resd": "Research Device",
    "rnlw": "Regulation or Law",
    "sbst": "Substance",
    "shro": "Self-help or Relief Organization",
    "socb": "Social Behavior",
    "sosy": "Sign or Symptom",
    "spco": "Spatial Concept",
    "tisu": "Tissue",
    "tmco": "Temporal Concept",
    "topp": "Therapeutic or Preventive Procedure",
    "virs": "Virus",
    "vita": "Vitamin",
    "vtbt": "Vertebrate"
};

const semTypeAbrvToCategory = {
    "aapp": "Substance",
    "acab": "Anatomical Structure",
    "acty": "Activity",
    "aggp": "Group",
    "amas": "Idea or Concept",
    "amph": "Organism",
    "anab": "Anatomical Structure",
    "anim": "Organism",
    "anst": "Anatomical Structure",
    "antb": "Substance",
    "arch": "Organism",
    "bacs": "Substance",
    "bact": "Organism",
    "bdsu": "Substance",
    "bdsy": "Idea or Concept",
    "bhvr": "Activity",
    "biof": "Phenomenon or Process",
    "Organism": "Bird",
    "blor": "Idea or Concept",
    "bmod": "Occupation or Discipline",
    "bodm": "Substance",
    "bpoc": "Anatomical Structure",
    "bsoj": "Idea or Concept",
    "celc": "Anatomical Structure",
    "celf": "Phenomenon or Process",
    "cell": "Anatomical Structure",
    "cgab": "Anatomical Structure",
    "chem": "Substance",
    "chvf": "Substance",
    "chvs": "Substance",
    "clas": "Intellectual Product",
    "clna": "Organism Attribute",
    "clnd": "Manufactured Object",
    "cnce": "Conceptual Entity",
    "comd": "Phenomenon or Process",
    "crbs": "Idea or Concept",
    "diap": "Activity",
    "dora": "Activity",
    "drdd": "Manufactured Object",
    "dsyn": "Phenomenon or Process",
    "edac": "Activity",
    "eehu": "Phenomenon or Process",
    "elii": "Substance",
    "emod": "Phenomenon or Process",
    "emst": "Anatomical Structure",
    "enty": "Entity",
    "enzy": "Substance",
    "euka": "Organism",
    "evnt": "Event",
    "famg": "Group",
    "ffas": "Anatomical Structure",
    "fish": "Organism",
    "fndg": "Finding",
    "fngs": "Organism",
    "food": "Substance",
    "ftcn": "Idea or Concept",
    "genf": "Phenomenon or Process",
    "geoa": "Idea or Concept",
    "gngm": "Anatomical Structure",
    "gora": "Activity",
    "grpa": "Group Attribute",
    "grup": "Group",
    "hcpp": "Phenomenon or Process",
    "hcro": "Organization",
    "hlca": "Activity",
    "hops": "Substance",
    "horm": "Substance",
    "humn": "Organism",
    "idcn": "Idea or Concept",
    "imft": "Substance",
    "inbe": "Activity",
    "inch": "Substance",
    "inpo": "Phenomenon or Process",
    "inpr": "Intellectual Product",
    "irda": "Indicator, Reagent, or Diagnostic Aid",
    "lang": "Language",
    "lbpr": "Activity",
    "lbtr": "Finding",
    "mamm": "Organism",
    "mbrt": "Activity",
    "mcha": "Activity",
    "medd": "Manufactured Object",
    "menp": "Phenomenon or Process",
    "mnob": "Manufactured Object",
    "mobd": "Phenomenon or Process",
    "moft": "Phenomenon or Process",
    "mosq": "Idea or Concept",
    "neop": "Phenomenon or Process",
    "nnon": "Substance",
    "npop": "Phenomenon or Process",
    "nusq": "Idea or Concept",
    "ocac": "Activity",
    "ocdi": "Occupation or Discipline",
    "orch": "Substance",
    "orga": "Organism Attribute",
    "orgf": "Phenomenon or Process",
    "orgm": "Organism",
    "orgt": "Organization",
    "ortf": "Phenomenon or Process",
    "patf": "Phenomenon or Process",
    "phob": "Physical Object",
    "phpr": "Phenomenon or Process",
    "phsf": "Phenomenon or Process",
    "phsu": "Substance",
    "plnt": "Organism",
    "podg": "Group",
    "popg": "Group",
    "prog": "Group",
    "pros": "Organization",
    "qlco": "Idea or Concept",
    "qnco": "Idea or Concept",
    "rcpt": "Substance",
    "rept": "Organism",
    "resa": "Activity",
    "resd": "Manufactured Object",
    "rnlw": "Intellectual Product",
    "sbst": "Substance",
    "shro": "Organization",
    "socb": "Activity",
    "sosy": "Finding",
    "spco": "Idea or Concept",
    "tisu": "Anatomical Structure",
    "tmco": "Idea or Concept",
    "topp": "Activity",
    "virs": "Organism",
    "vita": "Substance",
    "vtbt": "Organism"
}

const semTypesCategories = [
    "Activity",
    "Anatomical Structure",
    "Conceptual Entity",
    "Finding",
    "Group",
    "Group Attribute",
    "Intellectual Product",
    "Language",
    "Manufactured Object",
    "Occupation or Discipline",
    "Organism",
    "Organism Attribute",
    "Organization",
    "Phenomenon or Process",
    "Substance",
]

const semTypeCategoriesToColor = {
"Activity": "#000075",
"Anatomical Structure": "#808000",
"Conceptual Entity": "#ffd8b1",
"Finding": "#bfef45",
"Group": "#911eb4",
"Group Attribute": "#f032e6",
"Idea or Concept": "#123512",
"Intellectual Product": "#a9a9a9",
"Language": "#fabed4",
"Manufactured Object": "#4363d8",
"Occupation or Discipline": "#ffe119",
"Organism": "#800000",
"Organism Attribute": "#e6194B",
"Organization": "#aaffc3",
"Phenomenon or Process": "#469990",
"Substance": "#f58231",
}

function sem_types_abrv_to_text(sem_types) {
    return sem_types.map(sem_type => semTypesAbrvToFull[sem_type]).join(' | ');
}

function sem_type_abrv_to_text(sem_type) {
    return semTypesAbrvToFull[sem_type];
}

function get_sem_types() {
    return Object.keys(semTypesAbrvToFull);
}

function get_number_of_sem_types() {
    return Object.keys(semTypesAbrvToFull).length;
}

function getSemCategories() {
    return semTypesCategories;
}

function getSemCategoriesNum() {
    return semTypesCategories.length;
}

function getSemCategoryFromAbrv(sem_type) {
    return semTypeAbrvToCategory[sem_type];
}

function getColorForSemTypeCategory(semTypeCategory) {
    return semTypeCategoriesToColor[semTypeCategory];
}


function getColorForSemTypeAbrv(semTypeAbrv) {
    return semTypeCategoriesToColor[getSemCategoryFromAbrv(semTypeAbrv)]
}
