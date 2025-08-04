sfdx force:auth:web:login --alias metaprod --instance-url https://login.salesforce.com --set-default  
pause
sfdx force:data:soql:query -q "SELECT count(id),MethodName,ApexClass.name,status FROM AsyncApexJob WHERE CreatedDate = LAST_N_DAYS:3    group by MethodName,ApexClass.name,status order by count(id) desc " -r csv >> C:\Muneesh\Monitor\SyncApexJobs_output.csv
pause