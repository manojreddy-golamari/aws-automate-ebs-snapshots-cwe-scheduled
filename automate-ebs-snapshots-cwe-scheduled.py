import json
import boto3
from pprint import pprint

def lambda_handler(event, context):
    
    ec2= boto3.client('ec2')
    
    tags={'Name': 'tag:Backup','Values': ['True']}
    
    #getting the vloume ids present in ebs volume section 
    
    get_volumes= ec2.describe_volumes()['Volumes']
    get_volumes_ids=[]
    for volumes in get_volumes:
        get_volumes_ids.append(volumes['VolumeId'])
    
    print('Available & In-use Volumes list is in below:')
    print(get_volumes_ids)
    
    print('*******************' * 10)
    
    volumes=ec2.describe_volumes(Filters=[tags])['Volumes']
    
    #collecting the volumeids based on tags
    volume_ids=[]
    
    for volume in volumes:
        volume_ids.append(volume['VolumeId'])
    
    print('Printing the tags based on tags',tags['Name'],tags['Values'])
    print(volume_ids)
    
    for id in volume_ids:
    
        createSnapshot=ec2.create_snapshot(
            Description='Creating the snapshot for prod EBS volume by lambda scheduled cloudwatch events.',
            VolumeId=id,
            TagSpecifications=[
                {
                    'ResourceType': 'snapshot',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': id
                        },
                    ]
                },
            ]
        )
        print("Snapshot is In-progress for volume id :",id)
        print("Snapshot ID is :",createSnapshot['SnapshotId'])
        print('*******************' * 10)
        
        #sending the email with the ebs volume snapshot details
        
        ses=boto3.client('ses')
        
        #getting the info
        
        volume_ID=createSnapshot['VolumeId']
        volume_Size=createSnapshot['VolumeSize']
        snapshot_ID=createSnapshot['SnapshotId']
        snapshot_start=createSnapshot['StartTime']
        state=createSnapshot['State']
        Encryption=createSnapshot['Encrypted']
        description=createSnapshot['Description']
    
        #source Email
        source_Email='balafrancismanojreddy@gmail.com'
        
        #destination Email
        destination_Email='francismanojreddy@gmail.com'
        
        #cc Email
        cc_Email='balafrancismanojreddy@gmail.com'
        
        #subject of the Email
        Subject ='Prod EBS Volume SNAPSHOT'
        
        #body of the email
        Body='''
                <br>
                Hello Team, 
                <br>
                <br>
                This Email is regarding the EBS SNAPSHOT for volume <b> {vid}.</b>.
                <br>
                <br>
                Below are the details. 
                <br>
                Please take a look at high priority.
                <br>
                <b>volume ID</b>: {vid} <br>
                <b>volume Size </b> :{vsize}GB<br>
                <b>snapshot ID</b>:{snapid} <br>
                <b>snapshot start Time </b>:{snapstart} <br>
                <b>state</b>:{sstate} <br>
                <b>Encryption</b>:{encrpt} <br>
                <b>Description</b>:{des} <br>
                <br>
                <br>
                <br>
                <b>
                Thanks & Regards,
                <br>
                G B F Manoj Reddy
                </b>
            '''.format(vid=volume_ID,vsize=volume_Size,snapid=snapshot_ID,snapstart=snapshot_start,sstate=state,encrpt=Encryption,des=description)
        message={
                'Subject': {
                    'Data': Subject,
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Html': {
                        'Data': Body,
                        'Charset': 'UTF-8'
                    }
                }
            }
        response = ses.send_email(Source=source_Email,Destination={
                'ToAddresses': [
                    destination_Email,
                ],
                'CcAddresses': [
                    cc_Email,
                ]},Message=message)
                        
            
    return {
        'statusCode': 200,
        'body': json.dumps('Snapshot is In-progress!')
    }
