#!/usr/bin/env python
from troposphere import Base64, Parameter, Output, Ref, Template, Join
from troposphere.events import Rule, Target
from troposphere.iam import Role, InstanceProfile, Policy as tPolicy
from awacs.aws import Allow, Statement, Principal, Policy, Action
from awacs.sts import AssumeRole
import troposphere.ec2 as ec2

import collections
from ansible import utils, errors
import json
import yaml
import sys
from ansible.module_utils.basic import *

#import boto3
import json
from troposphere import awsencode

def create_instance(template,parameters=None,user_data_script=None,assign_public_ip=None,volume=None,profile=None):
    image_id = parameters['image_id']
    key_name = parameters['key_name']
    sg_ids = parameters['sg_ids']
    instance_type = parameters['instance_type']
    subnet_id = parameters['subnet_id']

    content = []
    user_data=None
    if user_data_script:
        with open(user_data_script, 'r') as f:
            content = f.readlines()
        user_data = Base64(Join('', content))

    ec2_instance = template.add_resource(ec2.Instance(
        "Ec2Instance",
        ImageId=Ref(image_id),
        InstanceType=Ref(instance_type),
        KeyName=Ref(key_name)
    ))

    if assign_public_ip:
        ec2_instance.NetworkInterfaces=[
            ec2.NetworkInterfaceProperty(
                AssociatePublicIpAddress=True,
                DeviceIndex=0,
                GroupSet=Ref(sg_ids),
                SubnetId=Ref(subnet_id)
            )
        ]
    else:
        ec2_instance.SecurityGroupIds=Ref(sg_ids)
        ec2_instance.SubnetId=Ref(subnet_id)

    if volume:
        ec2_instance.BlockDeviceMappings=[ec2.BlockDeviceMapping(
            DeviceName='/dev/sda1',
            Ebs=volume
        )]

    if profile:
        ec2_instance.IamInstanceProfile=Ref(profile)

    if user_data:
        ec2_instance.UserData=user_data

def create_volume(template,vol_type='gp2',vol_size=8,delete_on_term=None):
    dev = ec2.EBSBlockDevice(
        VolumeType=vol_type,
        VolumeSize=vol_size
    )
    if delete_on_term:
        dev.DeleteOnTermination=delete_on_term

    return dev



def create_schedule():
    print("test")


def create_parameters(template):
    key_name = template.add_parameter(Parameter(
        "KeyName",
        Description="Name of an existing EC2 KeyPair to enable SSH "
                    "access to the instance",
        Type="AWS::EC2::KeyPair::KeyName",
    ))
    instance_type = template.add_parameter(Parameter(
        "InstanceType",
        Description="EC2 Instance Type",
        Type="String",
    ))
    image_id = template.add_parameter(Parameter(
        "AMI",
        Description="AMI",
        Type="AWS::EC2::Image::Id",
    ))
    subnet_id = template.add_parameter(Parameter(
        "SubnetId",
        Description="Subnet ID",
        Type="AWS::EC2::Subnet::Id",
    ))
    sg_ids = template.add_parameter(Parameter(
        "SecurityGroupIds",
        Description="Security Group IDs",
        Type="List<AWS::EC2::SecurityGroup::Id>"
    ))

    parameters = {
        "image_id" : image_id,
        "key_name" : key_name,
        "instance_type" : instance_type,
        "subnet_id" : subnet_id,
        "sg_ids" : sg_ids
    }
    return parameters

def create_iam_policy(template,role_name,policy_name,role_path,policy_document,profile_name):
    cfnrole = template.add_resource(Role(
        role_name,
        AssumeRolePolicyDocument=Policy(
        Statement=[
            Statement(
                Effect=Allow,
                Action=[AssumeRole],
                Principal=Principal("Service", ["ec2.amazonaws.com"])
            )
        ]),
        Path=role_path,
        Policies=[
            tPolicy(
                PolicyName=policy_name,
                PolicyDocument=json.loads(policy_document)
            )
        ]
    ))


    cfninstanceprofile = template.add_resource(InstanceProfile(
        profile_name,
        Roles=[Ref(cfnrole)]
    ))
    return cfninstanceprofile


def main():
  module = AnsibleModule(
    argument_spec = dict(
      ec2_role_name  = dict(required=False, type='str'),
      ec2_role_profile_name = dict(required=False, type='str'),
      ec2_role_path = dict(required=False, type='str'),
      ec2_role_policy_document = dict(required=False, type='str'),
      ec2_role_policy_name = dict(required=False, type='str'),
      ec2_user_data_script_file = dict(required=False, type='str'),
      ec2_assign_public_ip = dict(reqired=False, type='bool'),
      ec2_create_volume = dict(required=False, type='bool' ),
      ec2_vol_type = dict(required=False, type='str'),
      ec2_vol_size = dict(required=False, type='int'),
      ec2_vol_delete_on_term = dict(required=False, type='bool')
    )
  )

  # IAM Policies
  user_data_script = module.params.get('ec2_user_data_script_file')
  role_profile_name = module.params.get('ec2_role_profile_name')
  role_name = module.params.get('ec2_role_name')
  role_path = module.params.get('ec2_role_path')
  role_policy_document = module.params.get('ec2_role_policy_document')
  role_policy_name =  module.params.get('ec2_role_policy_name')

  # Auto Assign Public IP
  assign_public_ip = module.params.get('ec2_assign_public_ip')

  # Volume
  create_vol = module.params.get('ec2_create_volume')
  vol_size = module.params.get('ec2_vol_size')
  vol_type = module.params.get('ec2_vol_type')
  delete_on_term = module.params.get('ec2_vol_delete_on_term')

  template = Template()
  parameters = create_parameters(template)
  vol = None
  if create_vol:
      vol = create_volume(template,vol_size=vol_size,vol_type=vol_type,delete_on_term=delete_on_term)

  profile = None
  if role_policy_document:
      profile = create_iam_policy(template,role_name,role_policy_name,role_path,role_policy_document,role_profile_name)

  create_instance(template,parameters=parameters,user_data_script=user_data_script,assign_public_ip=assign_public_ip,volume=vol,profile=profile)


  module.exit_json(
        Changed=False,
        Failed=False,
        Result=template.to_json()
  )

if __name__ == "__main__":
    main()
