#!python3


import boto3

import ec2
import sys
import datetime






# モニタリング情報取得
cli = boto3.client("cloudwatch")
response = cli.get_metric_statistics(
    Namespace='AWS/EC2',
    # MetricName='CPUUtilization',
    MetricName='CPUCreditBalance',
    Dimensions=[
        {
            'Name': 'InstanceId',
            'Value': 'i-0eaafd6dd07e51b43'
        },
    ],
    StartTime=datetime.datetime.utcnow() - datetime.timedelta(seconds=300),
    EndTime=datetime.datetime.utcnow(),
    Period=300,
    # Statistics=['Average']
    Statistics=['Minimum']
)

print(response)

for res in response['Messages']:
    if 'Body' in res:
        print(res['Body'])

sys.exit()





# ターゲットグループへインスタンスを追加
def add_instance_targetgroup(arn, instance_id, port):
    lb = boto3.client('elbv2')
    target = { "id": instance_id, "Port": port }
    lb.register_targets(TargetGroupArn=arn, Targets=[target])



# LB一覧
lb = boto3.client('elbv2')
ret = lb.describe_load_balancers()
for item in ret.get('LoadBalancers'):
    print(item.get('LoadBalancerArn'))

print()

# ターゲットグループ一覧
ret_tg = lb.describe_target_groups()
for item in ret_tg.get('TargetGroups'):
    print(item.get('TargetGroupName'), item.get('TargetGroupArn'))
    res_health = lb.describe_target_health(TargetGroupArn=item.get('TargetGroupArn'))
    # print(res_health)
    for desc in res_health.get('TargetHealthDescriptions'):
        id = desc.get('Target').get('Id')
        ec2_obj = ec2.ec2()
        print(id , "/", ec2_obj.get_info(id).name)
        port = desc.get('Target').get('Port')
        print(port)
        status = desc.get('TargetHealth').get('State')
        print(status)


# print(ret)
# lb.describe_target_groups()