aws cloudtrail lookup-events --lookup-attributes AttributeKey=Username,AttributeValue=matias.desanti
> /home/delivery/Programming/proton/conf/AWS/cloudtrail_lookup-events.json

aws cloudtrail lookup-events --lookup-attributes AttributeKey=EventName,AttributeValue=AuthorizeSecurityGroupIngress
> /home/delivery/Programming/proton/conf/AWS/cloudtrail_lookup-event-by-event

$ aws cloudtrail lookup-events --start-time 2017-03-08T20:40:00.000Z --end-time 2017-03-08T21:20:00.000Z
--lookup-attributes AttributeKey=EventName,AttributeValue=AuthorizeSecurityGroupIngress
> /home/delivery/Programming/proton/conf/AWS/cloudtrail_lookup-event-by-event-with-time.json