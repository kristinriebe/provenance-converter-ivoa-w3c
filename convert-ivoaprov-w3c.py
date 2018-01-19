import argparse
import json
from pprint import pprint

"""
A simple converter from IVOA to W3C compatible provenance
serialization (PROV-JSON format).
This currently probably only works with serializations
extracted from the ProvDAL prototype at
https://escience.aip.de/provenance-rave/prov_vo/provdal/
(status: 19th January 2018).

It is not complete, i.e. not all classes and attributes
are converted (yet), but at least you will get a warning
for each class that cannot be mapped.
"""

# Here is a simple dictionary for mapping provenance attribute names,
# from IVOA ProvenanceDM to W3C PROV-DM.
# This assumes that "voprov" is the prefix for the VO namespace and
# "prov" is the prefix for the W3C provenance namespace.
#
# TODO: do a proper namespace resolution!
#
# Note: this just maps the names of each attribute, but actually the
# datatypes and values have to be adjusted as well!
#
# TODO: Provide proper conversion functions for each attribute, that
#   requires some kind of conversion
#

ATTRIBUTE_MAPPING = {
    'activity': {
        'voprov:id': 'prov:id',
        'voprov:name': 'prov:label',
        'voprov:type': 'prov:type',
        'voprov:annotation': 'prov:description',
        'voprov:startTime': 'prov:startTime',
        'voprov:endTime': 'prov:endTime',
    },
    'entity': {
        'voprov:id': 'prov:id',
        'voprov:name': 'prov:label',
        'voprov:type': 'prov:type', # possibly also adjust the values! (prov:entity, prov:collection)
        'voprov:annotation': 'prov:description',
    },
    'agent': {
        'voprov:id': 'prov:id',
        'voprov:name': 'prov:label',
        'voprov:type': 'prov:type', # TODO: also adjust the values!!
    },
    'used': {
        'voprov:activity': 'prov:activity',
        'voprov:entity': 'prov:entity',
        'voprov:role': 'prov:role',
    },
    'wasGeneratedBy': {
        'voprov:entity': 'prov:entity',
        'voprov:activity': 'prov:activity',
        'voprov:role': 'prov:role',
    },
    'wasAssociatedWith': {
        'voprov:activity': 'prov:activity',
        'voprov:agent': 'prov:agent',
        'voprov:role': 'prov:role'
    },
    'wasAttributedTo': {
        'voprov:entity': 'prov:entity',
        'voprov:agent': 'prov:agent',
        #'voprov:role': 'voprov:role' # stays the same, because there is no prov:role in wasAttributedTo in W3C model
    },
    'hadMember': {
        'voprov:collection': 'prov:collection',
        'voprov:entity': 'prov:entity'
    },
    'wasInfluencedBy': {
        'voprov:activityFlow': 'prov:influencee',
        'voprov:activity': 'prov:influencer'  # this is the substep, pointing to the flow
    },
    'wasDerivedFrom': {
        'voprov:generatedEntity': 'prov:generatedEntity',
        'voprov:usedEntity': 'prov:usedEntity'
    },
    'wasInformedBy': {
        'voprov:informed': 'prov:informed',
        'voprov:informant': 'prov:informant'
    }
    # TODO: mapping for parameters and descriptions!
}

# Some classes need to be rewritten as well
CLASS_MAPPING = {
    'activityFlow': {
        'w3c_class': 'activity',
        'votype': 'voprov:activityFlow'
    },
    'hadStep': {
        'w3c_class': 'wasInfluencedBy',
        'votype': 'voprov:hadStep'
    },
    # collection in W3C is not really an own class, but rather an entity
    # with type "prov:collection"
    'collection': {
        'w3c_class': 'entity',
        'type': 'prov:collection'
    }
}

def main():

    parser = argparse.ArgumentParser(description="Convert IVOA provenance serialization (PROV-JSON) to W3C compatible serialization")
    parser.add_argument('filename', type=str, help="Name of PROV-JSON file")
    args = parser.parse_args()

    filename = args.filename
    outfilename = filename.replace('.json', '-w3c.json')
    print('Reading file %s.' % outfilename)

    vo_data = json.load(open(filename))

    w3c_data = {}
    for classname, vo_instances in vo_data.items():
        class_votype = None
        class_type = None
        if classname in CLASS_MAPPING:
            w3c_classname = CLASS_MAPPING[classname]['w3c_class']
            if 'votype' in CLASS_MAPPING[classname]:
                class_votype = CLASS_MAPPING[classname]['votype']
            if 'type' in CLASS_MAPPING[classname]:
                class_type = CLASS_MAPPING[classname]['type']
        else:
            # class name does not need to be changed
            w3c_classname = classname
        w3c_instances = {}
        if w3c_classname in ATTRIBUTE_MAPPING:
            for vo_instance, attributes in vo_instances.items():
                w3c_instance = {}
                for vo_name, value in attributes.items():
                    if vo_name in ATTRIBUTE_MAPPING[w3c_classname]:
                        w3c_name = ATTRIBUTE_MAPPING[w3c_classname][vo_name]
                    else:
                        w3c_name = vo_name
                    w3c_instance[w3c_name] = value
                if class_votype:
                    w3c_instance['votype'] = class_votype  # TODO: check, if votype already exists!
                if class_type:
                    w3c_instance['type'] = class_type  # TODO: BE CAREFUL: This may overwrite already existing type values!
                w3c_instances[vo_instance] = w3c_instance
            # check if dict-entry for this possibly mapped classname already exists, then append, else just add
            if w3c_classname in w3c_data:
                w3c_data[w3c_classname].update(w3c_instances)
            else:
                w3c_data[w3c_classname] = w3c_instances
        else:
            # Assume, that no special mapping is needed, just copy everything
            print("Warning: No mapping found for class %s. Will just assume that no conversion is needed and copy everything." % classname)
            w3c_data[classname] = vo_instances

    with open(outfilename, 'w') as outfile:
       json.dump(w3c_data, outfile, indent=4)

    print('Provenance metadata were converted to W3C compatible serialization and exported as PROV-JSON to %s.' % outfilename)

if __name__ == '__main__':
    main()