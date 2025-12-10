import boto3

profile = 'default'

def secgroup_loop():
    intro = """
    Welcome to BXPawsSec
    A tool for manipulating AWS Security Groups.

    Type 'help' for the help menu."""

    print(intro)
    
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
                menu = list()
            case _:
                if ans.isdigit():
                    if ans in menu:
                        workWithSecgroup(menu[ans]['id'])
                        #menu = list()
                    else:
                        print('Unknow menu item')    
                else:
                    print('Please choose a number')

    
def workWithSecgroup(id):
    while(1):
        ans = input(id + '> ')
        match ans:
            case 'help':
                print('list         - list rules for this group')
                print('delete rule  - delete a rule')
                print('add rule     - add a rule')
                print('delete group - delete the current group')
                print('quit         - escape this submenu')
            case 'quit':
                break
            case 'exit':
                print('exit program')
                exit(0)
            #This is really dangerous, so I am commenting it
            #out. Uncomment if you know what you are doing.
            #
            # case 'delete group':
            #     ans = input('Type \'delete\' to delete this group: ')
            #     if ans == 'delete':
            #         ret = deleteSg(id)
            #         if ret == True:
            #             break
            #     else:
            #         print('Not deleting group')
            case 'list':
                r_list = listRulesDisplay(id)
            case 'delete rule':
                delRule(id)
            case 'add rule':
                addRule(id)

                
def addRule(sg_id):
    session = boto3.session.Session(profile_name=profile)
    client = session.client('ec2')
    
    ip = input('IP address: ')

    if '/' not in ip:
        ip += '/32'

    port = input('port(443): ')
    if(port == ''):
        port = 443
        
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
        
    
def listRulesDisplay(sg_id, rules_list={}, count=1, token=None):
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
       
            MaxResults=20
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
            MaxResults=20
        )

    print('\n')

    for rule in rules['SecurityGroupRules']:
        desc = ''
        if 'Description' in rule:
           desc = rule['Description']

           rules_list[str(count)] = {
            'id':rule['SecurityGroupRuleId'],
            'ip':rule['CidrIpv4'],
            'to_port':rule['ToPort'],
            'proto':rule['IpProtocol'],
           }

  
           rules_list[str(count)]['desc'] = rule['Description']

        print(f'{count}: {rule["CidrIpv4"]} {rule["IpProtocol"]} {rule["ToPort"]:<10} {desc}')
        count += 1

    ans = input('Enter to move on \'stop\' to quit) ')
    if ans == 'stop':
        return rules_list
    
    if 'NextToken' not in rules:
        return rules_list
   
    return listRulesDisplay(sg_id, rules_list, count, rules['NextToken'])


def delRule(sg_id):
    session = boto3.session.Session(profile_name=profile)
    client = session.client('ec2')

    rules = listRulesDisplay(sg_id)

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
                response = client.revoke_security_group_ingress(
                    SecurityGroupRuleIds = [
                        rules[rule_ans]['id']
                    ],
                    GroupId = sg_id
                )
    

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
