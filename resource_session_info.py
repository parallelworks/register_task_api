import requests
import os
from functools import partial

import pandas as pd

N_PARSED_PROPERTIES: int = 2
CLIENT_HOST: str = os.environ['PARSL_CLIENT_HOST']
KEY: str = os.environ['PW_API_KEY']
USER: str = os.environ['PW_USER']

CONTROLLER_PROPERTIES_MAPPING: dict = {
    'gclusterv2': {
        'management_shape ': 'instance_type ',
        'controller_tier_1 ': 'high_performance_networking '
    },
    'pclusterv2': {
        'management_shape ': 'instance_type ',
        'controller_efa ': 'high_performance_networking '
    }
}

PARTITION_PROPERTIES_MAPPING: dict = {
    'gclusterv2': {
        'management_shape ': 'instance_type ',
        'tier_1 ': 'high_performance_networking '
    },
    'pclusterv2': {
        'management_shape ': 'instance_type ',
        'efa ': 'high_performance_networking '
    }
}

def get_controller_lines(properties_lines):
    controller_lines = []
    for line in properties_lines:
        if 'partition_config' in line:
            return controller_lines
        controller_lines.append(line)

def get_partition_lines(properties_lines, partition):
    partition_lines = []
    parition_config = False
    partition_found = False
    for line in properties_lines:
        if 'partition_config' in line:
            parition_config = True

        if not parition_config:
            continue

        if '{' in line:
            partition_lines = []

        if 'name' in line:
            if partition in line:
                partition_found = True

        partition_lines.append(line)

        if '}' in line:
            if partition_found:
                return partition_lines


def get_properties_from(properties_lines):
    properties = {}
    missing_properties = N_PARSED_PROPERTIES

    for line in properties_lines:
        if 'instance_type' in line:
            properties['instance_type'] = line.replace(" ", "").replace('"', '').split('=')[1]
            missing_properties += -1
        elif 'high_performance_networking' in line:
            properties['high_performance_networking'] = bool(line.replace(" ", "").replace('"', '').split('=')[1])
            missing_properties += -1
            
        if missing_properties == 0:
            return properties


def get_properties_lines(name, session):
    url = f'https://{CLIENT_HOST}/api/v2/proxy/usercontainer?proxyType=api&proxyTo=/api/v1/display/pw/.pools/{USER}/{name}/{session}/pool.properties&key={KEY}'
    return requests.get(url).text.split('\n')

def get_provider(properties_lines):
    for line in properties_lines:
        if 'provider' in line:
            return line.split('=')[1]

def get_properties(name, session, get_lines, mapping):
    properties_lines = get_properties_lines(name, session)
    provider = get_provider(properties_lines)
    properties_lines = get_lines(properties_lines)
    properties_lines = '\n'.join(properties_lines)
    for orig,new in mapping[provider].items():
        properties_lines = properties_lines.replace(orig, new)
    properties_lines = properties_lines.split('\n')
    return get_properties_from(properties_lines)


# Define a function to apply get_partition_properties to each row of the dataframe
def get_properties_apply(row):
    name = row['name']
    session = "{:05d}".format(row['session'])
    partition = row['partition']
    if partition:
        get_lines = partial(get_partition_lines, partition = partition)
        properties_dict = get_properties(name, session, get_lines, PARTITION_PROPERTIES_MAPPING)
    else:
        properties_dict = get_properties(name, session, get_controller_lines, CONTROLLER_PROPERTIES_MAPPING)

    return pd.Series(properties_dict, name=f"{partition}_properties")

if __name__ == '__main__':
    name = 'gcpslurmv2dev'
    session = 95
    partition = 'compute'
    name = 'awsv2'
    session = 4

    df = pd.DataFrame({'name': [name], 'session': [session], 'partition': [partition]})
    print(df)
    properties_df = df.apply(get_properties_apply, axis=1)
    print(properties_df)