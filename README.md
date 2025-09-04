# BXPawsSEC #
(Pronounced BoxPawsSec)

This is a reeeeeally rough bit of code. I only meant it for 
some of the work I do and not for much more. So this code is
somewhat customized to my needs

I thought I would share it just in case someone needed 
some examples on using boto3.

It works with your aws security groups, allowing you to add
new ones, delete old ones and add rules. This allows me
to add ingress rules for users needing access to private 
resources and removing them when no longer needed.

## But, why? ##

I created another program with the ability to handle a lot more 
AWS functionality. 

I created this one because I hadn't imported that code to my github 
repo and I was stuck on another computer. I wanted to continue 
working on the program I started, so I made this using code I 
wanted to import into the stand alone program.

I decided to make this one standalone just for fun.

I've tried to include some help menus so you aren't totally
blind.

You will need to setup your aws configuration file with a profile
you can use in this program. I assume 'default', but you can change
that to whatever profile name you choose. If you don't know how
to get your aws environment set up, you'll need to figure that out
on your own.

## [WARNING: You are messing with your AWS account. Make REALLY sure of what you are doing and what to expect from this program. USE AT YOUR OWN RISK. You've been warned.] ##


