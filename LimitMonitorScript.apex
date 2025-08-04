Map<String,System.OrgLimit> limitsMap = OrgLimits.getMap();
System.OrgLimit apiRequestsLimit = limitsMap.get('DailyAsyncApexExecutions');
System.debug('Limit Name: ' + apiRequestsLimit.getName());
System.debug('Usage Value: ' + apiRequestsLimit.getValue());
System.debug('Maximum Limit: ' + apiRequestsLimit.getName());
String s = '';
s += 'Limit Name '+ ' , ' + 'Limit Maximum '+ ' , ' + 'Limit Used '+  '\n\n';
s += apiRequestsLimit.getName() + ' , ' + apiRequestsLimit.getName() + ' , ' + apiRequestsLimit.getValue() + '\n';



HttpRequest req = new HttpRequest();
        Http http = new Http();
        req.setMethod('GET');
        String url = System.URL.getSalesforceBaseURL().toExternalForm() +'/services/data/v46.0/limits';
        req.setHeader('Authorization', 'OAuth ' + UserInfo.getSessionId());
		req.setHeader('Content-Type', 'application/json'); 
         req.setHeader('accept', 'application/json');
        req.setEndpoint(url);
        HttpResponse Resp =  http.send(req);     
	public String MMax;
    public String MRemaining;    
Map<String, Object> objmap =    (Map<String, Object>)   JSON.deserializeUntyped(Resp.getBody());
    system.debug('=== objmap : '+objmap);
public class MLimit {
    public String Max;
    public String Remaining;
}
String s = '';
s += 'Limit Name '+ ' , ' + 'Limit Maximum '+ ' , ' + 'Limit Remaining '+  '\n\n';
for (string key : objmap.keyset())
{
    if (key== 'SingleEmail' )
    {
     String valJson = JSON.serialize(objmap.get(key));  
     
     MLimit ml = (MLimit)JSON.deserializeStrict(valJson,MLimit.class);
        if (Integer.valueof(ml.Remaining.trim()) < 10000)
        {
          s += key + ' , ' + ml.max + ' , ' + ml.Remaining + '\n';
		  MMax=ml.max;
		  MRemaining=ml.Remaining;
        }
        system.debug('==Remaining == : '+ Integer.valueof(ml.Remaining.trim()));
    } 
}
System.debug('Email : '+ s );
Messaging.EmailFileAttachment csvAttc = new Messaging.EmailFileAttachment();
           	blob csvBlob = Blob.valueOf(s);
            string csvname=  'PROD_ImportantLimits As Of '+system.now()+'.csv';
            csvAttc.setFileName(csvname);
            csvAttc.setBody(csvBlob);
            Messaging.SingleEmailMessage email =new Messaging.SingleEmailMessage();
            String[] toAddresses = new list<string> {UserInfo.getUserEmail()};
			toAddresses.add('shanavas_yoosuff@mcafee.com');
            String subject ='SFDC PROD Limits : Maximum : '+ MMax + ' / Remaining : '+ MRemaining;
			
            email.setSubject(subject);
            email.setToAddresses( toAddresses );
            email.setPlainTextBody(s);
           // email.setFileAttachments(new Messaging.EmailFileAttachment[]{csvAttc});
            Messaging.SendEmailResult [] r = Messaging.sendEmail(new Messaging.SingleEmailMessage[] {email});
