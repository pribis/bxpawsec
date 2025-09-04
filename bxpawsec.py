import boto3

profile = 'default'

def secgroup_loop():
    menu = {}
    while(1):
        ans = input('> ')
        match ans:
            case 'help':
                print('list rules - list security groups')
                print('add rule - add new security group')
                print('exit - exit program')
                print('quit - exit submenu (or exit program if at the root menu - i.e., this one)')

            case 'exit':
                exit(0)
            case 'quit':
                exit(0)
            case 'list':
                menu = list()
            case 'add rule':
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
                print('del rule - delete this security group')
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
                listRulesDisplay(id)
            case 'del rule':
                delRule(id)
            case 'add rule':
                addRule(id)

                
def addRule(sg_id):
    session = boto3.session.Session(profile_name=profile)
    client = session.client('ec2')
    
    ip = input('IP address: ')

    if '/' not in ip:
        ip += '/32'

    port = input('port: ')
    proto = input('protocol(tcp): ')
    if proto == '':
        proto = 'tcp'
        
    desc = input('description: ')
    response = client.authorize_security_group_ingress(
        GroupId=sg_id,
        IpPermissions=[
            {
                'IpProtocol':proto,
                'FromPort':int(port),
                'ToPort':int(port),
                'IpRanges':[
                    {
                        'Description':desc,
                        'CidrIp':ip,
                    }]
            }]

    )
        
    
def listRulesDisplay(sg_id, token=None):
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
        desc = ''
        if 'Description' in rule:
           desc = rule['Description']
           
        print(f'{desc} {rule["CidrIpv4"]} {rule["IpProtocol"]} {rule["ToPort"]}')

    ans = input('Enter to move on (\'quit\' to stop) ')
    if ans == 'quit':
        return
    
    if 'NextToken' not in rules:
        return
    
    listRulesDisplay(sg_id, rules['NextToken'])

def delRule(sg_id):
    session = boto3.session.Session(profile_name=profile)
    client = session.client('ec2')
    rules = getRules(sg_id)
    

    rule_ans = input('Rule to delete: ')
    if rule_ans.isdigit():
        ans = input('Type \'delete\' to delete rule: ')
        if ans != 'delete':
            print('Not deleting rule')
            return
        else:
            if rule_ans not in rules:
                print('Unknown rule. Not deleting')
                return
            else:
                #Delete rule in rules[rule_ans]['id']
                response = client.revoke_security_group_ingress(
                    SecurityGroupRuleIds = [
                        rules[rule_ans]['id']
                    ],
                    GroupId = sg_id
                )
    
def getRules(sg_id):
    session = boto3.session.Session(profile_name=profile)
    client = session.client('ec2')

    rules = client.describe_security_group_rules(
        Filters=[
            {
                'Name':'group-id',
                'Values':[sg_id]
            }
        ],
    )

    count = 1
    list_rules = {}
    for rule in rules['SecurityGroupRules']:
        desc = ''
        if 'Description' in rule:
            desc = rule['Description']

        list_rules[str(count)] = {
            'id':rule['SecurityGroupRuleId'],
            'ip':rule['CidrIpv4'],
            'to_port':rule['ToPort'],
            'proto':rule['IpProtocol'],

        }

        if 'Description' in rule:
            list_rules[str(count)]['desc'] = rule['Description']
        count += 1

    for r in list_rules:
        desc = ''
        if 'desc' in list_rules[r]:
            desc = list_rules[r]['desc']
            
        print(f'{r} {list_rules[r]["ip"]} {desc}')



    return list_rules



def addSg():
    session = boto3.session.Session(profile_name=profile)
    client = session.client('ec2')
    vpc = getVpc()
    if vpc == False or vpc == '':
        print('Creating of security group failed')
        return False

    name = input('Name: ')
    desc = input('Description: ')
    if name and desc:
        ret = client.create_security_group(
            Description=desc,
            GroupName=name,
            VpcId=vpc
        )
    else:
        print('Not creating security group')
    
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
