# ansible-role-module-troposphere-ec2

## Role Parameters

| Variable        | Required           | Default  | Description |
| ------------- |:-------------:| ---------:| -------------------------------------------------------------------------:|
| ec2_stack_name | yes | | Name of the CloudFormation stack |
| ec2_ami | yes | | AMI for the instance |
| ec2_subnet_id | yes | | Subnet ID where the EC2 instance will be placed |
| ec2_instance_type | yes | | EC2 instance type |
| ec2_sgs | yes | | Security group ids to use with EC2 instance |
| ec2_region | no | us-west-2 | Region to deploy into |
| ec2_create_volume | no | False | Create a EBS block device for the instance |
| ec2_vol_size | no | 8 (GB) | If creating an EBS block device for the instance, the size of the volume |
| ec2_user_data_script_file | no | | If you wish to provide User Data, load contents of this file into the User Data |
| ec2_assign_public_ip | no | False | Automatically assign a public IP to the instance |
| ec2_security_token | no | | Optionally provide a security token for deploying the instance via ansible |
| ec2_role_name | no | |  If the instance will be assuming a role, you may supply a role name (logical ID) |
| ec2_role_policy_name | no | EC2RolePolicy | If the instance will be assuming a role, you may supply a role policy name (logical ID) |
| ec2_role_path | no | / |  If the instance will be assuming a role, you may supply a role path (logical ID) |
| ec2_role_profile_name | no | EC2InstanceProfile | If the instance will be assuming a role, you may supply the instance profile name (logical ID) |
| ec2_build_dir | no | ./build | You may supply an alternate directory for build artifacts if so desired |

## Example Playbook Using Role
```
- hosts: localhost
  vars:
    ec2_stack_name: "trop-test"
    ec2_ami: "ami-12345678"
    ec2_subnet_id: "subnet-12345678"
    ec2_role_path: "/testing/"
    ec2_key_name: "test-key"
    ec2_instance_type: "t2.nano"
    ec2_security_token: "{{ lookup('env','AWS_SESSION_TOKEN') }}"
    ec2_sgs: "sg-12345678"
    ec2_user_data_script_file: "user_data.sh"
    ec2_create_volume: True
    ec2_assign_public_ip: True
    ec2_vol_size: 25
    ec2_tags:
      "test": test
    ec2_role_policy_document: " { \"Version\": \"2012-10-17\",\"Statement\": [ { \"Effect\": \"Allow\", \"Action\" : [ \"s3:GetObject\", \"s3:PutObject\", \"s3:ListBucket\" ], \"Resource\" : \"arn:aws:s3:::test-bucket/*\" } ] }"
  roles:
    - ec2_trop
```

## Example Playbook Using Module
```
- hosts: localhost
  vars:
    ec2_stack_name: "trop-test"
    ec2_ami: "ami-12345678"
    ec2_subnet_id: "subnet-12345678"
    ec2_role_path: "/testing/"
    ec2_key_name: "test-key"
    ec2_instance_type: "t2.nano"
    ec2_security_token: "{{ lookup('env','AWS_SESSION_TOKEN') }}"
    ec2_sgs: "sg-12345678"
    ec2_user_data_script_file: "user_data.sh"
    ec2_create_volume: True
    ec2_assign_public_ip: True
    ec2_vol_size: 25
    ec2_tags:
      "test": test
    ec2_role_policy_document: " { \"Version\": \"2012-10-17\",\"Statement\": [ { \"Effect\": \"Allow\", \"Action\" : [ \"s3:GetObject\", \"s3:PutObject\", \"s3:ListBucket\" ], \"Resource\" : \"arn:aws:s3:::test-bucket/*\" } ] }"\"arn:aws:s3$
  tasks:
    - name: Run troposphere to generate template
      troposphere_ec2:
        ec2_role_name: "{{ ec2_role_name }}"
        ec2_role_policy_document: "{{ ec2_role_policy_document }}"
        ec2_role_policy_name: "{{ ec2_role_policy_name | default(omit, true) }}"
        ec2_role_path: "{{ ec2_role_path | default(omit, true) }}"
        ec2_role_profile_name: "{{ ec2_role_profile_name }}"
        ec2_user_data_script_file: "{{ ec2_user_data_script_file | default(omit, true) }}"
        ec2_assign_public_ip: "{{ ec2_assign_public_ip | bool }}"
        ec2_create_volume: "{{ ec2_create_volume | bool }}"
        ec2_vol_size: "{{ ec2_vol_size }}"
        ec2_vol_type: "{{ ec2_vol_type }}"
      register: result

```
