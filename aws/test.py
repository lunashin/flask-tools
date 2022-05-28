#!python3


import boto3




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

# ターゲットグループ一覧
ret_tg = lb.describe_target_groups()
for item in ret_tg.get('TargetGroups'):
    print(item.get('TargetGroupArn'), item.get('TargetGroupName'))


# print(ret)
# lb.describe_target_groups()