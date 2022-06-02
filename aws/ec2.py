#!python3

import boto3
import sys
import datetime





###########################################
# Class
###########################################

# EC2
class ec2:
    resource = None # ec2 Resource
    records = None  # ec2_records

    def __init__(self) -> None:
        records = None
        self.resource = boto3.resource('ec2')

    # インスタンスリストを取得
    # return: ec2_record[]
    # 
    def get_all(self) -> list:
        self.records = ec2_records()
        self.records.make_from_resource(self.resource)
        return self.records.records

    # 稼働中インスタンスリスト
    def get_running(self) -> list:
        all_ins = self.get_all()

        # 稼働中のみ抽出
        ret = []
        for item in all_ins:
            if item.isRunning():
                ret.append(item)
        return ret

    # 停止中インスタンスリスト
    def get_stopped(self) -> list:
        all_ins = self.get_all()

        # 停止中のみ抽出
        ret = []
        for item in all_ins:
            if item.isStopped():
                ret.append(item)
        return ret

    # 稼働中/停止中以外のインスタンスリスト
    def get_not_running_or_stopped(self) -> list:
        all_ins = self.get_all()

        # 稼働中のみ抽出
        ret = []
        for item in all_ins:
            if not item.isRunning() and not item.isStopped():
                ret.append(item)
        return ret

    # インスタンス情報取得
    def get_info(self, instance_id:str):
        instance = self.resource.Instance(instance_id)
        record = ec2_record()
        record.make_from_resource(instance)
        return record

    # インスタンス作成
    def create_instance(self, name, instance_type, image_id, security_group_id, keypair_name):
        tag = {'Key': 'Name', 'Value': name}
        tags = {'ResourceType': "instance", 'Tags': [tag]}
        ins_list = self.resource.create_instances(ImageId=image_id, InstanceType=instance_type, SecurityGroupIds=[security_group_id], TagSpecifications=[tags], KeyName=keypair_name, MaxCount=1, MinCount=1)

    # インスタンス作成（デフォルト設定）
    def create_instance_preset(self, name):
        dt_now = datetime.datetime.now()
        name = name + " " + dt_now.strftime('%Y%m%d-%H%M%S') + " Created by Flask"
        instance_type = 't2.small'
        image_id = 'ami-00bc9b7f0e98dc134'
        security_group_id = 'sg-b5bc00d2'
        self.create_instance(name, instance_type, image_id, security_group_id)

    # インスタンスタイプ変更
    def change_instance_type(self, instance_id, instance_type):
        instance = self.resource.Instance(instance_id)
        res = instance.modify_attribute(InstanceType={'Value': instance_type})


# EC2 (low api ver)
class ec2_low:
    client = None
    records = None

    def __init__(self) -> None:
        self.client = boto3.client('ec2')
        self.records = None

    def get_all(self):
        response = self.client.describe_instances()
        # print(response)
        self.records = ec2_records()
        self.records.make_from_response(response)

    def get_running(self):
        response = self.client.describe_instances(Filters=[{'Name': 'instance-state-name','Values': ['running']}])
        self.records = ec2_records()
        self.records.make_from_response(response)

    def get_stopped(self):
        response = self.client.describe_instances(Filters=[{'Name': 'instance-state-name','Values': ['stopped']}])
        self.records = ec2_records()
        self.records.make_from_response(response)

    def start(self, instance_id):
        resp = self.client.start_instances(InstanceIds=[instance_id])

    def stop(self, instance_id):
        resp = self.client.stop_instances(InstanceIds=[instance_id])

    def terminate(self, instance_id):
        resp = self.client.terminate_instances(InstanceIds=[instance_id])


# EC2レコード一覧
class ec2_records:
    records = None      # ec2_record[]

    def __init__(self) -> None:
        self.records = []

    # リソースをパース
    def make_from_resource(self, resource):
        for instance in resource.instances.all():
            item = ec2_record()
            item.make_from_resource(instance)
            if item.isValid():
                self.records.append(item)

    # レスポンスをパース
    def make_from_response(self, response):
        for resv in response['Reservations']:
            item = ec2_record()
            item.make_from_response(resv)
            if item.isValid():
                self.records.append(item)


# EC2レコード
class ec2_record:
    name = ""
    instance_id = ""
    public_ip = ""
    private_ip = ""
    state = ""
    instance_type = ""
    image_id = ""
    security_groups = None

    def __init__(self) -> None:
        pass

    # リソースをパース
    def make_from_resource(self, instance):
        # EC2.Instance オブジェクト
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#instance
        self.state = instance.state.get('Name')

        # 削除済みの場合は終わり
        if self.state == 'terminated':
            return

        if instance.tags != None:
            for tag in instance.tags:
                key = tag.get('Key')
                if key == 'Name':
                    self.name = tag.get('Value')

        self.instance_id = instance.instance_id
        self.public_ip = instance.public_ip_address
        self.private_ip = instance.private_ip_address
        self.instance_type = instance.instance_type
        self.image_id = instance.image_id
        self.security_groups = instance.security_groups

    # レスポンスをパース
    def make_from_response(self, reservation):
        state_root = instances_dict.get('State')
        if state_root != None:
            self.state = state_root.get('Name')

        # 削除済みの場合は終わり
        if self.state == 'terminated':
            return

        instances_dict = reservation.get('Instances')[0]

        for tag in instances_dict['Tags']:
            if tag.get('Key') == "Name":
                self.name = tag.get('Value')
                break
        self.instance_id = instances_dict.get('InstanceId')
        self.public_ip = instances_dict.get('PublicIpAddress')
        self.private_ip = instances_dict.get('PrivateIpAddress')

    # 有効なデータかどうか
    def isValid(self):
        return self.state != 'terminated'

    # ステータスが running かどうか
    def isRunning(self) -> bool:
        return self.state == 'running'
    # ステータスが stopped かどうか
    def isStopped(self) -> bool:
        return self.state == 'stopped'

    # メンバ表示
    def show(self):
        print(self.name,    self.instance_id,    self.public_ip,    self.private_ip,    self.state, self.image_id)
        print(self.security_groups)
        






# obj = ec2()
# obj.get_all()
