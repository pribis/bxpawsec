import boto3

profile = 'brian'

def secgroup_loop():
    menu = {}
    while(1):
        ans = input('> ')
        match ans:
            case 'help':
                print('list - list security groups')
                print('add  - add new security group')
                print('exit - exit program')
                print('quit - exit submenu (or exit program if at the root menu - i.e., this one)')

            case 'exit':
                exit(0)
            case 'quit':
                exit(0)
            case 'list':
                menu = list()
            case 'add':
                addSg()
            case _:
                if ans.isdigit():
                    if ans in menu:
                        workWithSecgroup(menu[ans]['id'])
                    else:
                        print('Unknow menu item')    
                else:
                    print('Please choose a number')

    
def workWithSecgroup(id):
    while(1):
        ans = input(id + '> ')
        match ans:
            case 'help':
                print('list rules - list rules for this group')
                print('delete - delete this security group')
                print('quit   - escape this submenu')
            case 'quit':
                break
            case 'exit':
                print('exit program')
                exit(0)
            case 'delete':
                ans = input('Type \'delete\' to delete this group: ')
                if ans == 'delete':
                    ret = deleteSg(id)
                    if ret == True:
                        break
                else:
                    print('Not deleting group')
            case 'list rules':
                listRules(id)

def addRule(sg_id):
    ip = input('IP address: ')
    port = input('port: ')
    proto = input('protocall: ')
    desc = input('description: ')
  
def listRules(sg_id, token=None):
    session = boto3.session.Session(profile_name=profile)
    client = session.client('ec2')

    if token == None:
        rules = client.describe_security_group_rules(
            Filters=[
                {
                    'Name':'group-id',
                    'Values':[sg_id]
                }
            ],
       
            MaxResults=10
        )
    else:
        rules = client.describe_security_group_rules(
            Filters=[
                {
                    'Name':'group-id',
                    'Values':[sg_id]
                }
            ],
            NextToken=token,
            MaxResults=10
        )
    for rule in rules['SecurityGroupRules']:
        if 'Description' in rule:
            print(rule['Description'])
        print(rule['ToPort'])
        print(rule['IpProtocol'])
        print(rule['CidrIpv4'])
        print('-----------------')

    input('Enter to move on')
    if 'NextToken' not in rules:
        return
    listRules(sg_id, rules['NextToken'])

    
def addSg():
    session = boto3.session.Session(profile_name=profile)
    client = session.client('ec2')
    vpc = getVpc()
    if vpc == False or vpc == '':
        print('Creating of security group failed')
        return False

    print("Creating using vpc " + vpc)
    ret = client.create_security_group()
    
def getVpc():
    session = boto3.session.Session(profile_name=profile)
    client = session.client('ec2')
    vpcs = client.describe_vpcs()

    count = 1
    menu = {}
    for vpc in vpcs['Vpcs']:
        name = ''
        for tag in vpc['Tags']:
            name = tag['Value']
            break
        menu[str(count)] = {'id':vpc['VpcId'], 'name':name}
        count += 1

    for m in menu:
        print(m + ' ' + menu[m]['name'] + ' (' + menu[m]['id'] + ')')

    ans = input('Choose VPC: ')
    if ans == '':
        return False
    
    if ans.isdigit():
        if ans in menu:
            return menu[ans]['id']
        else:
            print('Unknown vpc')
            return False
    else:
        print('Not a number')
        return False
    
    return False
    
def deleteSg(id):
    session = boto3.session.Session(profile_name=profile)
    client = session.client('ec2')
    res = client.delete_security_group(GroupId=id)
    if res['Return'] == True:
        print('Group deleted')
        return True
    else:
        print('Group deleting failed')
        return False

def list():
    session = boto3.session.Session(profile_name=profile)
    client = session.client('ec2')
    res = client.describe_security_groups()

    count = 1
    menu = {}
    for sg in res['SecurityGroups']:
        menu[str(count)] = {'id':sg["GroupId"], 'name':sg["GroupName"]}
        count += 1

    for m in menu:
        print(m + " " + menu[m]['name'] + " (" + menu[m]['id'] + ")") 

    return menu
                            
                            

    
def main():
    secgroup_loop()

if __name__ == '__main__':
    main()
