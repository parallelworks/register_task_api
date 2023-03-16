import requests
import os
from dataclasses import dataclass, field

N_PARSED_ATTRIBUTES: int = 2
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


def get_attributes_value(properties_lines):
    attributes = {}
    missing_attributes = N_PARSED_ATTRIBUTES

    for line in properties_lines:
        if 'instance_type' in line:
            attributes['instance_type'] = line.replace(" ", "").replace('"', '').split('=')[1]
            missing_attributes += -1
        elif 'high_performance_networking' in line:
            attributes['high_performance_networking'] = bool(line.replace(" ", "").replace('"', '').split('=')[1])
            missing_attributes += -1
            
        if missing_attributes == 0:
            return attributes


def get_properties_lines(name, session):
    url = f'https://{CLIENT_HOST}/api/v2/proxy/usercontainer?proxyType=api&proxyTo=/api/v1/display/pw/.pools/{USER}/{name}/{session}/pool.properties&key={KEY}'
    return requests.get(url).text.split('\n')

def get_provider(properties_lines):
    for line in properties_lines:
        if 'provider' in line:
            return line.split('=')[1]

def get_controller_attributes(name, session):
    properties_lines = get_properties_lines(name, session)
    provider = get_provider(properties_lines)
    properties_lines = get_controller_lines(properties_lines)
    properties_lines = '\n'.join(properties_lines)
    for orig,new in CONTROLLER_PROPERTIES_MAPPING[provider].items():
        properties_lines = properties_lines.replace(orig, new)
    properties_lines = properties_lines.split('\n')
    return get_attributes_value(properties_lines)


def get_partition_attributes(name, session, partition):
    properties_lines = get_properties_lines(name, session)
    provider = get_provider(properties_lines)
    properties_lines = get_partition_lines(properties_lines, partition)
    properties_lines = '\n'.join(properties_lines)
    for orig,new in PARTITION_PROPERTIES_MAPPING[provider].items():
        properties_lines = properties_lines.replace(orig, new)
    properties_lines = properties_lines.split('\n')
    return get_attributes_value(properties_lines)


name = 'gcpslurmv2dev'
session = '00095'
partition = 'compute'

aux = get_controller_attributes(name, session)
print(aux)

aux = get_partition_attributes(name, session, partition)
print(aux)

name = 'awsv2'
session = '00002'

aux = get_controller_attributes(name, session)
print(aux)

aux = get_partition_attributes(name, session, partition)
print(aux)